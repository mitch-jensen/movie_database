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

    try:
        yield testinfra.get_host("docker://" + container.id)
    finally:
        container.remove(force=True)


@pytest.fixture
def versioned_python_dependencies(host: Host) -> list[str]:
    return host.check_output("python -m pip freeze").split("\n")


@pytest.fixture
def python_dependencies(versioned_python_dependencies: list[str]) -> list[str]:
    return [d.split("==")[0] for d in versioned_python_dependencies]


def test_production_dependencies_are_installed(python_dependencies: list[str]):
    expected_dependencies = ["Django", "uvicorn", "django-ninja", "pydantic", "psycopg"]
    assert set(expected_dependencies).issubset(python_dependencies)


def test_development_dependencies_are_not_installed(python_dependencies: list[str]):
    unexpected_dependencies = ["beartype", "commitizen", "deptry", "model-bakery", "pre-commit", "pytest", "pytest-django", "ruff"]
    assert set(unexpected_dependencies).isdisjoint(python_dependencies)


def test_test_dependencies_are_not_installed(python_dependencies: list[str]):
    unexpected_dependencies = ["docker", "pytest-testinfra"]
    assert set(unexpected_dependencies).isdisjoint(python_dependencies)
