from hibob_monitor.cli import (
    OutputFormat,
    StdOutOutputInfo,
    SupportedBrowser,
    create_argument_parser,
)


def test_parser_accepts_domain() -> None:
    parser = create_argument_parser()
    args = parser.parse_args(["--domain", "acme.hibob.com"])
    assert args.domain == "acme.hibob.com"


def test_parser_defaults() -> None:
    parser = create_argument_parser()
    args = parser.parse_args(["--domain", "acme.hibob.com"])
    assert args.browser == SupportedBrowser.FIREFOX
    assert args.format == OutputFormat.TABLE
    assert args.stdout_output == StdOutOutputInfo.CHANGES


def test_parser_opts() -> None:
    parser = create_argument_parser()
    args = parser.parse_args(
        [
            "--domain",
            "acme.hibob.com",
            "--browser",
            "chrome",
            "--format",
            "json",
            "--stdout-output",
            "employee_list",
        ]
    )
    assert args.browser == SupportedBrowser.CHROME
    assert args.format == OutputFormat.JSON
    assert args.stdout_output == StdOutOutputInfo.EMPLOYEE_LIST
