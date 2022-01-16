"""Our setup script."""

import glob
from setuptools import setup

setup(
    name="wmb",
    description="Watching MrBayes",
    packages=["wmb"],
    package_data={"wmb": ["data/*"]},
    scripts=glob.glob("wmb/scripts/*.sh"),
    entry_points={"console_scripts": ["wmb=wmb.cli:safe_cli"]},
    install_requires=[
        "jinja2",
        "seqmagick",
    ],
)
