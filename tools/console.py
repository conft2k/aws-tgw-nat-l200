"""Drive the AWS console (English) for rehearsal and screenshots.

    uv run --with playwright --with boto3 python tools/console.py <script.py>

The script file is executed with `page`, `shot(name)`, `goto(path)` and
`mask()` in scope. Login: GetFederationToken for the IAM user of
$AWS_PROFILE, then a federation sign-in URL. The browser storage state is kept
in $CONSOLE_STATE (default: a file outside the repo) so later runs reuse the
session. Screenshots go to docs/images/console/<name>.png with the account ID
replaced by 111122223333.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import boto3
from playwright.sync_api import sync_playwright

PROFILE = os.environ.get("AWS_PROFILE", "sandbox")
REGION = os.environ.get("AWS_REGION", "ap-northeast-2")
STATE = Path(os.environ.get("CONSOLE_STATE", Path.home() / ".cache/tgwnat-console-state.json"))
ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "docs/images/console"
FAKE = "111122223333"


def signin_url() -> str:
    s = boto3.Session(profile_name=PROFILE, region_name=REGION)
    account = s.client("sts").get_caller_identity()["Account"]
    policy = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}
    creds = s.client("sts").get_federation_token(
        Name="workshop-user", Policy=json.dumps(policy), DurationSeconds=43200)["Credentials"]
    session = json.dumps({"sessionId": creds["AccessKeyId"], "sessionKey": creds["SecretAccessKey"],
                          "sessionToken": creds["SessionToken"]})
    q = urllib.parse.urlencode({"Action": "getSigninToken", "SessionDuration": 43200, "Session": session})
    token = json.load(urllib.request.urlopen(f"https://signin.aws.amazon.com/federation?{q}"))["SigninToken"]
    dest = f"https://{REGION}.console.aws.amazon.com/console/home?region={REGION}"
    q = urllib.parse.urlencode({"Action": "login", "Issuer": "tgwnat-workshop", "Destination": dest,
                                "SigninToken": token})
    os.environ["TGWNAT_ACCOUNT"] = account
    return f"https://signin.aws.amazon.com/federation?{q}"


def main() -> int:
    script = Path(sys.argv[1]).read_text()
    account = boto3.Session(profile_name=PROFILE).client("sts").get_caller_identity()["Account"]
    dashed = f"{account[:4]}-{account[4:8]}-{account[8:]}"
    SHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx_args = {"viewport": {"width": 1440, "height": 900}, "locale": "en-US",
                    "device_scale_factor": 1}
        if STATE.exists():
            ctx_args["storage_state"] = str(STATE)
        ctx = browser.new_context(**ctx_args)
        page = ctx.new_page()
        page.set_default_timeout(45000)

        cur = {"page": page}

        def P():
            return cur["page"]

        def use(p):
            """Point goto/shot/mask at another tab (e.g. the EC2 Instance Connect terminal)."""
            cur["page"] = p

        def goto(path: str):
            url = path if path.startswith("http") else f"https://{REGION}.console.aws.amazon.com{path}"
            P().goto(url, wait_until="domcontentloaded")
            if "signin.aws.amazon.com" in P().url or "/oauth" in P().url:
                P().goto(signin_url(), wait_until="domcontentloaded")
                P().wait_for_url(re.compile(r".*console\.aws\.amazon\.com.*"), timeout=60000)
                P().goto(url, wait_until="domcontentloaded")
            P().wait_for_load_state("load", timeout=60000)
            P().wait_for_timeout(4000)  # the console keeps polling; never networkidle
            close_tours()

        def close_tours():
            # first-visit console tours ("Service menu" etc.) and info banners
            for _ in range(6):
                t = P().locator('[data-testid^="awsc-nav-services-tooltip"] button, [data-testid*="tooltip-confirm"]')
                vis = [x for x in t.all() if x.is_visible()]
                if not vis:
                    break
                vis[-1].click(timeout=3000)
                P().wait_for_timeout(500)
            for x in P().get_by_role("button", name=re.compile(r"^(Dismiss|Close)( notification)?$")).all():
                try:
                    if x.is_visible():
                        x.click(timeout=2000)
                except Exception:
                    pass

        def frames():
            return [f for f in P().frames if not f.is_detached()]

        def app():
            # the frame that holds the console page body (VPC console uses an iframe)
            best, size = P().main_frame, -1
            for f in frames():
                if "lotus/" in f.url or "continuum." in f.url:
                    continue  # console nav / search widgets
                try:
                    n = len(f.locator("body").inner_text(timeout=3000))
                except Exception:
                    continue
                if f is not P().main_frame and n > size:
                    best, size = f, n
            return best if size > 200 else P().main_frame

        def all_text():
            out = []
            for f in frames():
                try:
                    out.append(f.locator("body").inner_text(timeout=3000))
                except Exception:
                    pass
            return "\n".join(out)

        def mask():
            for f in frames():
                try:
                    mask_frame(f)
                except Exception:
                    pass
            digits = re.sub(r"[\s\-\u00a0]", "", all_text())
            if account in digits:
                raise RuntimeError("account ID still visible on the page; screenshot refused")

        def mask_frame(frame):
            # account ID in any spacing (plain, dashed, split across spans) -> FAKE
            frame.evaluate(
                """([a, f]) => {
                  const re = new RegExp(a.split('').join('[\\s\\-\\u00a0]?'), 'g');
                  const fd = f.slice(0,4)+'-'+f.slice(4,8)+'-'+f.slice(8);
                  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                  let n; while ((n = w.nextNode())) {
                    if (re.test(n.nodeValue)) { re.lastIndex = 0; n.nodeValue = n.nodeValue.replace(re, m => m.includes('-') ? fd : f); }
                    re.lastIndex = 0;
                  }
                  for (const el of document.querySelectorAll('input, textarea')) {
                    if (el.value && re.test(el.value)) { re.lastIndex = 0; el.value = el.value.replace(re, f); }
                    re.lastIndex = 0;
                  }
                }""",
                [account, FAKE])

        secrets = [x for x in os.environ.get("CONSOLE_SECRETS", "").split(",") if x]

        def mask_secrets():
            if secrets:
              for fr in frames():
               try:
                fr.evaluate(
                    """(ss) => {
                      const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                      let n; while ((n = w.nextNode())) for (const s of ss)
                        if (n.nodeValue.includes(s)) n.nodeValue = n.nodeValue.split(s).join('(hidden)');
                      for (const el of document.querySelectorAll('input, textarea')) for (const s of ss)
                        if (el.value.includes(s)) el.value = el.value.split(s).join('(hidden)');
                    }""", secrets)
               except Exception:
                pass
              if any(x in all_text() for x in secrets):
                    raise RuntimeError("secret still visible on the page; screenshot refused")

        def shot(name: str, locator=None, clip=None, margin: int = 16):
            """Full-window original to shots/raw, cropped (clip locator or box) to docs/images."""
            mask()
            mask_secrets()
            path = SHOTS / f"{name}.png"
            raw = ROOT / "shots/raw/console" / f"{name}.png"
            raw.parent.mkdir(parents=True, exist_ok=True)
            if locator is not None:
                locator.scroll_into_view_if_needed()
                mask()
                mask_secrets()
            P().screenshot(path=str(raw))
            box = None
            if clip is not None and not isinstance(clip, (tuple, list)):
                clip.scroll_into_view_if_needed()
                mask()
                mask_secrets()
                P().screenshot(path=str(raw))
                bb = clip.bounding_box()
                if bb:
                    vw = P().viewport_size
                    box = (max(0, bb["x"] - margin), max(0, bb["y"] - margin),
                           min(vw["width"], bb["x"] + bb["width"] + margin),
                           min(vw["height"], bb["y"] + bb["height"] + margin))
            elif clip is not None:
                box = tuple(clip)
            if box:
                P().screenshot(path=str(path), clip={"x": box[0], "y": box[1],
                                                     "width": box[2] - box[0], "height": box[3] - box[1]})
            else:
                import shutil
                shutil.copy(raw, path)
            print(f"shot {path.relative_to(ROOT)}", flush=True)

        if not STATE.exists():
            page.goto(signin_url(), wait_until="domcontentloaded")
            page.wait_for_url(re.compile(r".*console\.aws\.amazon\.com.*"), timeout=60000)
        try:
            exec(script, {"page": page, "use": use, "app": app, "goto": goto, "close_tours": close_tours, "shot": shot, "mask": mask, "REGION": REGION, "re": re})
        finally:
            STATE.parent.mkdir(parents=True, exist_ok=True)
            ctx.storage_state(path=str(STATE))
            os.chmod(STATE, 0o600)
            browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
