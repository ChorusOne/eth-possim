from setuptools import find_packages, setup


with open("requirements.txt") as fl:
    requires = fl.readlines()


setup(
    name="eth_possim",
    version="0.1.0",
    description="""
Run full-featured Ethereum PoS simulator (private net) locally or in CI/CD,
with experimental PBS (MEV) emulation support.
    """,
    packages=find_packages(exclude=["ez_setup", "tests", "tests.*"]),
    include_package_data=True,
    install_requires=requires,
    python_requires="==3.11",
    author_email="opus@chorus.one",
)
