import pkg_resources

packages = ['flask', 'pandas', 'google-auth', 'google-api-python-client', 'twilio', 'requests', 'beautifulsoup4']

for package in packages:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f"{package}: {version}")
    except pkg_resources.DistributionNotFound:
        print(f"{package} is not installed")
