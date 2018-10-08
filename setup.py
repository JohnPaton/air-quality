from setuptools import setup


setup(
    name="air-quality",
    version="0.1.0",
    description="Processing and modelling tools for air quality prediction",
    author="John Paton",
    author_email="john@johnpaton.net",
    python_requires=">=3.6",
    packages=["air_quality"],
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "scipy",
        "requests",
        "flask",
        "tqdm",
    ],
)
