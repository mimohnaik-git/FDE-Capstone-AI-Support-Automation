"""
Submission Package Creator for CloudServe Support Automation.
Packages all required artifacts into the 4 official submission directories and creates the final zip archive.
"""

import os
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
SUBMISSION_DIR = BASE_DIR / "submission_package"
ZIP_OUTPUT = BASE_DIR / "CloudServe_FDE_Capstone_Submission.zip"


def package_submission():
    """Assembles the final submission package."""
    print("Assembling final submission package...")

    # Clean existing directory
    if SUBMISSION_DIR.exists():
        shutil.rmtree(SUBMISSION_DIR)

    # 1. Create the 4 required top-level directories
    v_dir = SUBMISSION_DIR / "01_Video"
    r_dir = SUBMISSION_DIR / "02_Report"
    w_dir = SUBMISSION_DIR / "03_Workbooks"
    c_dir = SUBMISSION_DIR / "04_Source_Code"

    for d in [v_dir, r_dir, w_dir, c_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Copy Video script
    shutil.copy(BASE_DIR / "docs" / "video_presentation_script.md", v_dir / "video_presentation_script.md")

    # Copy Report
    shutil.copy(BASE_DIR / "docs" / "final_capstone_report.md", r_dir / "CloudServe_FDE_Capstone_Report.md")

    # Copy Workbooks & Effort Log
    wb_src = BASE_DIR / "capstone_pack" / "02_Stage_Workbooks"
    for item in wb_src.glob("*.docx"):
        shutil.copy(item, w_dir / item.name)

    eff_src = BASE_DIR / "capstone_pack" / "04_Submission" / "Effort_Log.docx"
    if eff_src.exists():
        shutil.copy(eff_src, w_dir / "Effort_Log.docx")

    # Copy Markdown workbook versions
    for md_file in (BASE_DIR / "docs").glob("stage_*.md"):
        shutil.copy(md_file, w_dir / md_file.name)
    if (BASE_DIR / "docs" / "effort_log.md").exists():
        shutil.copy(BASE_DIR / "docs" / "effort_log.md", w_dir / "effort_log.md")
    if (BASE_DIR / "docs" / "ai_use_declaration.md").exists():
        shutil.copy(BASE_DIR / "docs" / "ai_use_declaration.md", w_dir / "ai_use_declaration.md")

    # Copy Code Repository (src, tests, evaluation, data, docs, prompts, config)
    for folder in ["src", "tests", "evaluation", "data", "docs", "prompts"]:
        s_folder = BASE_DIR / folder
        if s_folder.exists():
            shutil.copytree(
                s_folder,
                c_dir / folder,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", ".pytest_cache", "*.sqlite", "*.sqlite-*"
                ),
            )

    for root_file in ["requirements.txt", "pytest.ini", "README.md", "CLAUDE.md", ".env.example"]:
        rf = BASE_DIR / root_file
        if rf.exists():
            shutil.copy(rf, c_dir / root_file)

    print(f"Submission directory assembled at {SUBMISSION_DIR}")

    # Create Zip Archive
    if ZIP_OUTPUT.exists():
        ZIP_OUTPUT.unlink()

    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(SUBMISSION_DIR):
            for file in files:
                full_path = Path(root) / file
                rel_path = full_path.relative_to(SUBMISSION_DIR)
                zf.write(full_path, arcname=rel_path)

    print(f"Final submission archive created: {ZIP_OUTPUT} ({ZIP_OUTPUT.stat().st_size / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    package_submission()
