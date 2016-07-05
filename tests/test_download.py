from py.path import local

from pokediadb.cli import pokediadb


def test_dl_pokedia_repo_with_correct_folder_path(runner, tmp_context):
    directory = tmp_context.mkdir("pokeapi_test")
    result = runner.invoke(pokediadb, ["download", str(directory)])
    assert result.exit_code == 0

    assert not directory.join("pokeapi").check()

    # Check for csv and sprites folder
    csv = directory.join("csv")
    sprites = directory.join("sprites")

    assert csv.check()
    assert len(csv.listdir()) > 0

    assert sprites.check()
    assert len(sprites.listdir()) > 0


def test_dl_pokedia_repo_with_incorrect_folder_path(runner):
    nonexistent_dir = local("/incorrect_path/684546")
    result = runner.invoke(pokediadb, ["download", str(nonexistent_dir)])
    assert 'Error: Invalid value for "path"' in result.output
    assert result.exit_code == 2

    assert not nonexistent_dir.join("pokeapi").check()
    assert not nonexistent_dir.join("csv").check()
    assert not nonexistent_dir.join("sprites").check()


def test_dl_pokedia_repo_without_path_argument(runner, tmp_context):
    result = runner.invoke(pokediadb, ["download"])
    assert result.exit_code == 0

    assert not tmp_context.join("pokeapi").check()

    # Check for csv and sprites folder
    csv = tmp_context.join("csv")
    sprites = tmp_context.join("sprites")

    assert csv.check()
    assert len(csv.listdir()) > 0

    assert sprites.check()
    assert len(sprites.listdir()) > 0


def test_dl_pokedia_repo_in_a_folder_already_containing_a_pokeapi_directory(
        runner, tmp_context):
    tmp_context.join("pokeapi").mkdir()
    result = runner.invoke(pokediadb, ["download", str(tmp_context)])
    assert result.exit_code == 1
    assert result.output.startswith("A pokeapi folder already exists")

    assert not tmp_context.join("csv").check()
    assert not tmp_context.join("sprites").check()
