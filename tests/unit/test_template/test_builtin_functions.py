import sys
from pathlib import Path
from typing import Optional

import pytest

from litestar import get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.contrib.mako import MakoTemplateEngine
from litestar.response.template import Template
from litestar.static_files.config import StaticFilesConfig
from litestar.status_codes import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from litestar.template.config import TemplateConfig
from litestar.testing import create_test_client


@pytest.mark.xfail(sys.platform == "win32", reason="For some reason this is flaky on windows")
def test_jinja_url_for(tmp_path: Path) -> None:
    template_config = TemplateConfig(engine=JinjaTemplateEngine, directory=tmp_path)

    @get(path="/")
    def tpl_renderer() -> Template:
        return Template(template_name="tpl.html")

    @get(path="/simple", name="simple")
    def simple_handler() -> None:
        pass

    @get(path="/complex/{int_param:int}/{time_param:time}", name="complex")
    def complex_handler() -> None:
        pass

    with create_test_client(
        route_handlers=[simple_handler, complex_handler, tpl_renderer], template_config=template_config, debug=True
    ) as client:
        Path(tmp_path / "tpl.html").write_text("{{ url_for('simple') }}")

        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "/simple"

    with create_test_client(
        route_handlers=[simple_handler, complex_handler, tpl_renderer], template_config=template_config
    ) as client:
        Path(tmp_path / "tpl.html").write_text("{{ url_for('complex', int_param=100, time_param='18:00') }}")

        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "/complex/100/18:00"

    with create_test_client(
        route_handlers=[simple_handler, complex_handler, tpl_renderer], template_config=template_config
    ) as client:
        # missing route params should cause 500 err
        Path(tmp_path / "tpl.html").write_text("{{ url_for('complex') }}")
        response = client.get("/")
        assert response.status_code == 500

    with create_test_client(
        route_handlers=[simple_handler, complex_handler, tpl_renderer], template_config=template_config
    ) as client:
        # wrong param type should also cause 500 error
        Path(tmp_path / "tpl.html").write_text("{{ url_for('complex', int_param='100', time_param='18:00') }}")

        response = client.get("/")
        assert response.status_code == 500

    with create_test_client(
        route_handlers=[simple_handler, complex_handler, tpl_renderer], template_config=template_config
    ) as client:
        Path(tmp_path / "tpl.html").write_text("{{ url_for('non-existent-route') }}")

        response = client.get("/")
        assert response.status_code == 500


@pytest.mark.xfail(sys.platform == "win32", reason="For some reason this is flaky on windows")
def test_jinja_url_for_static_asset(tmp_path: Path) -> None:
    template_config = TemplateConfig(engine=JinjaTemplateEngine, directory=tmp_path)

    @get(path="/", name="tpl_renderer")
    def tpl_renderer() -> Template:
        return Template(template_name="tpl.html")

    with create_test_client(
        route_handlers=[tpl_renderer],
        template_config=template_config,
        static_files_config=[StaticFilesConfig(path="/static/css", directories=[tmp_path], name="css")],
    ) as client:
        Path(tmp_path / "tpl.html").write_text("{{ url_for_static_asset('css', 'main/main.css') }}")

        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "/static/css/main/main.css"

    with create_test_client(
        route_handlers=[tpl_renderer],
        template_config=template_config,
        static_files_config=[StaticFilesConfig(path="/static/css", directories=[tmp_path], name="css")],
    ) as client:
        Path(tmp_path / "tpl.html").write_text("{{ url_for_static_asset('non-existent', 'main.css') }}")

        response = client.get("/")
        assert response.status_code == 500

    with create_test_client(
        route_handlers=[tpl_renderer],
        template_config=template_config,
        static_files_config=[StaticFilesConfig(path="/static/css", directories=[tmp_path], name="css")],
    ) as client:
        Path(tmp_path / "tpl.html").write_text("{{ url_for_static_asset('tpl_renderer', 'main.css') }}")

        response = client.get("/")
        assert response.status_code == 500


@pytest.mark.parametrize(
    "builtin, expected_status, expected_text",
    (
        ("${url_for_static_asset('css', 'main/main.css')}", HTTP_200_OK, "/static/css/main/main.css"),
        ("${url_for_static_asset('non-existent', 'main.css')}", HTTP_500_INTERNAL_SERVER_ERROR, None),
        ("${url_for_static_asset('tpl_renderer', 'main.css')}", HTTP_500_INTERNAL_SERVER_ERROR, None),
    ),
)
def test_mako_url_for_static_asset(
    tmp_path: Path, builtin: str, expected_status: int, expected_text: Optional[str]
) -> None:
    template_config = TemplateConfig(engine=MakoTemplateEngine, directory=tmp_path)

    @get(path="/", name="tpl_renderer")
    def tpl_renderer() -> Template:
        return Template(template_name="tpl.html")

    with create_test_client(
        route_handlers=[tpl_renderer],
        template_config=template_config,
        static_files_config=[StaticFilesConfig(path="/static/css", directories=[tmp_path], name="css")],
    ) as client:
        Path(tmp_path / "tpl.html").write_text(builtin)

        response = client.get("/")
        assert response.status_code == expected_status
        if expected_text:
            assert response.text == expected_text


@pytest.mark.parametrize(
    "builtin, expected_status, expected_text",
    (
        ("${url_for('simple')}", HTTP_200_OK, "/simple"),
        ("${url_for('complex', int_param=100, time_param='18:00')}", HTTP_200_OK, None),
        ("${url_for('complex')}", HTTP_500_INTERNAL_SERVER_ERROR, None),
        ("${url_for('non-existent-route')}", HTTP_500_INTERNAL_SERVER_ERROR, None),
    ),
)
def test_mako_url_for(tmp_path: Path, builtin: str, expected_status: int, expected_text: Optional[str]) -> None:
    template_config = TemplateConfig(engine=MakoTemplateEngine, directory=tmp_path)

    @get(path="/")
    def tpl_renderer() -> Template:
        return Template(template_name="tpl.html")

    @get(path="/simple", name="simple")
    def simple_handler() -> None:
        pass

    @get(path="/complex/{int_param:int}/{time_param:time}", name="complex")
    def complex_handler() -> None:
        pass

    with create_test_client(
        route_handlers=[simple_handler, complex_handler, tpl_renderer], template_config=template_config
    ) as client:
        # missing route params should cause 500 err
        Path(tmp_path / "tpl.html").write_text(builtin)
        response = client.get("/")
        assert response.status_code == expected_status
        if expected_text:
            assert response.text == expected_text
