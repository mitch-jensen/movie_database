from collections.abc import Generator

import pytest
import testinfra
from testinfra.host import Host

import docker
from docker.errors import ImageNotFound


# scope='session' uses the same container for all the tests;
# scope='function' uses a new container per test function.
@pytest.fixture(scope="session")
def host(request: pytest.FixtureRequest) -> Generator[Host]:
    client = docker.from_env()
    image_tag = "mitch-jensen/movie_database:ci"

    try:
        image = client.images.get(image_tag)
    except ImageNotFound:
        pytest.fail(f"Docker image '{image_tag}' not found. Did you forget to build it?")

    if type(image.id) is not str:
        pytest.fail(f"Docker image '{image}' is invalid.")

    container = client.containers.run(
        image=image.id,
        detach=True,
        tty=True,
    )

    if type(container.id) is not str:
        pytest.fail(f"Docker container '{container}' is invalid.")

    yield testinfra.get_host("docker://" + container.id)
    container.remove(force=True)


@pytest.mark.parametrize(
    "dependency",
    [
        "Django",
        "django-ninja",
        "uvicorn",
        "pydantic",
        "psycopg",
    ],
)
def test_production_dependencies_are_installed(host: Host, dependency: str):
    dependencies: dict[str, dict[str, str]] = host.pip.get_packages()
    assert dependency in dependencies


@pytest.mark.parametrize(
    "dependency",
    [
        "beartype",
        "commitizen",
        "deptry",
        "model-bakery",
        "pre-commit",
        "pytest",
        "pytest-django",
        "ruff",
    ],
)
def test_development_dependencies_are_not_installed(host: Host, dependency: str):
    dependencies: dict[str, dict[str, str]] = host.pip.get_packages()
    assert dependency not in dependencies


@pytest.mark.parametrize(
    "dependency",
    [
        "docker",
        "pytest-testinfra",
    ],
)
def test_test_dependencies_are_not_installed(host: Host, dependency: str):
    dependencies: dict[str, dict[str, str]] = host.pip.get_packages()
    assert dependency not in dependencies


def test_os_distribution_is_alpine(host: Host):
    assert host.system_info.distribution == "alpine"


def test_default_user_is_not_root_python_user(host: Host):
    user = host.user()
    assert user.name == "python"
    assert user.uid == 1000
    assert user.gid == 1000


@pytest.mark.parametrize(
    ("env_variable", "expected_value"),
    [
        ("DJANGO_SETTINGS_MODULE", "core.settings_production"),
        ("PYTHONUNBUFFERED", "1"),
        ("PYTHONDONTWRITEBYTECODE", "1"),
    ],
)
def test_environment_variables_are_as_expected(host: Host, env_variable: str, expected_value: str):
    environment: dict[str, str] = host.environment()
    assert environment[env_variable] == expected_value


# TODO @mitch-jensen: add more tests  # noqa: FIX002, TD003
# TODO @mitch-jensen: add host.file("/app").listdir() tests to assert folder structure  # noqa: FIX002, TD003
@pytest.mark.parametrize(
    "file_name",
    ["/app/requirements.txt"],
)
def test_files_exist(host: Host, file_name: str):
    file = host.file(file_name)
    assert file.exists
