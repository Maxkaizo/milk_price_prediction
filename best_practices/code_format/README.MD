# Code Formatting with Black

We applied the [Black](https://black.readthedocs.io/en/stable/) code formatter to enforce consistent, PEP8-compatible formatting across the project.

---

## ✅ Process Followed

For each folder:

1. **Checked formatting**:
   ```bash
   black <folder> --check --diff > best-practices/black_diff_<folder>.patch
```

2. **Applied formatting** if needed:

   ```bash
   black <folder>
   ```

3. **Saved actual diff** after applying:

   ```bash
   git diff > best-practices/black_applied_<folder>.patch
   ```

4. **Committed** changes with a clear message:

   ```bash
   git add <folder>
   git commit -m "Apply Black formatting to <folder>"
   ```

---

## 📁 Folders Processed

* `deployment/ondemand/`
* `iac/code/`
* `orchestration/`
* `simulate_publication/`

---

## 🔍 Notes

* All patches are stored in this folder for auditing purposes.
* No logic was changed—only formatting.
* Using `--check` and `--diff` allowed us to verify potential changes without applying them immediately.
* Manual patch review ensured full control over the formatting step before each commit.

---

## 💡 Recommendations

* Run `black .` before future commits or include it in a pre-commit hook.
* Keep formatting patches as documentation of code style enforcement.


