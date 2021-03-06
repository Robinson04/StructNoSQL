from setuptools import setup

setup(
    name="StructNoSQL",
    version="1.5.4",
    packages=["StructNoSQL", "StructNoSQL.dynamodb", "StructNoSQL.tables", "StructNoSQL.utils"],
    include_package_data=True,
    install_requires=["pydantic", "boto3"],
    url="https://github.com/Robinson04/StructNoSQL",
    license="MIT",
    author="Inoft",
    author_email="robinson@inoft.com",
    description="Structured document based NoSQL client for DynamoDB with automatic data validation and advanced database queries functions.",
)
