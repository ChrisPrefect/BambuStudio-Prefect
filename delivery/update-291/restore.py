import base64, hashlib, pathlib, subprocess
root = pathlib.Path(__file__).resolve().parent
parts = sorted(root.glob("source-*.b64"))
if len(parts) != 12: raise SystemExit("Expected exactly 12 reviewed bundle chunks")
data = base64.b64decode("".join(f.read_text(encoding="ascii").strip() for f in parts), validate=True)
if hashlib.sha256(data).hexdigest() != "e2f78bb7fbab3baab05ef076c09ae90e59174ec559cdf6b9b4128d5e3991d02a": raise SystemExit("Bundle checksum mismatch")
bundle = pathlib.Path(".git/prefect-update-291.bundle")
bundle.write_bytes(data)
subprocess.run(["git", "fetch", "--no-tags", "https://github.com/bambulab/BambuStudio.git", "tag", "v02.09.01.70"], check=True)
subprocess.run(["git", "bundle", "verify", str(bundle)], check=True)
subprocess.run(["git", "fetch", str(bundle), "HEAD"], check=True)
subprocess.run(["git", "checkout", "--detach", "322e1526180a6151dbc20622570881956dd5276b"], check=True)
tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], text=True).strip()
if tree != "ee22a0d76d2be8c3a6afb4a45737fda2cd78246d": raise SystemExit("Source tree mismatch")
print("Reviewed 2.9.1 source restored: 322e1526180a6151dbc20622570881956dd5276b", tree)

