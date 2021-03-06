#
#    Copyright (C) 2014 Alexandre Viau <alexandre@alexandreviau.net>
#
#    This file is part of python-pass.
#
#    python-pass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    python-pass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with python-pass.  If not, see <http://www.gnu.org/licenses/>.
#

import click
import os
import subprocess
import shutil


def git_add_and_commit(path, message=None):

    git_add = subprocess.Popen(['git', 'add', path], shell=False)
    git_add.wait()

    if message:
        git_commit = subprocess.Popen(
            ['git', 'commit', '-m', message], shell=False
        )
    else:
        git_commit = subprocess.Popen(['git', 'commit'], shell=False)

    git_commit.wait()


@click.group(invoke_without_command=True)
@click.option('--PASSWORD_STORE_DIR',
              envvar='PASSWORD_STORE_DIR',
              default=os.path.join(os.getenv("HOME"), ".password-store"),
              type=click.Path(file_okay=False, resolve_path=True))
@click.option('--PASSWORD_STORE_GIT',
              envvar='PASSWORD_STORE_GIT',
              type=click.STRING)
@click.pass_context
def main(ctx, password_store_dir, password_store_git):
    # Prepare the config file
    config = {
        'password_store_dir': password_store_dir
    }

    gpg_id_file = os.path.join(password_store_dir, '.gpg-id')
    if os.path.isfile(gpg_id_file):
        config['gpg-id'] = open(gpg_id_file, 'r').read()

    ctx.obj = config

    # Setup env vars
    os.environ['GIT_WORK_TREE'] = config['password_store_dir']

    if password_store_git:
        os.environ['GIT_DIR'] = password_store_git
    else:
        os.environ['GIT_DIR'] = \
            os.path.join(config['password_store_dir'], '.git')

    # By default, invoke ls
    if ctx.invoked_subcommand is None:
        ctx.invoke(ls)


@main.command()
@click.option('--path', '-p',
              type=click.Path(file_okay=False, resolve_path=True),
              default=os.path.join(os.getenv("HOME"), ".password-store"),
              help='Where to create the password store.')
@click.option('--clone', '-c',
              type=click.STRING,
              default=None,
              help='Git url to clone')
@click.argument('gpg-id', type=click.STRING)
def init(path, clone, gpg_id):
    # Do we have to add gpg-id ?
    add_gpg_id = True
    # Create a folder at the path
    if not os.path.exists(path):
        os.makedirs(path)

    # Clone an existing remote repo
    if clone is not None:
        # Init git repo
        git_result = subprocess.Popen(
            ["git", "init", path],
            shell=False,
        )
        git_result.wait()
        # Add remote repo
        git_result = subprocess.Popen(
            ["git", "remote", "add", "origin", clone],
            shell=False,
        )
        git_result.wait()
        # Pull remote repo
        # TODO: add parameters for remote and branch ?
        git_result = subprocess.Popen(
            ["git", "pull", "origin", "master"],
            shell=False,
        )
        git_result.wait()

    # check if gpgp id is already set
    with open(os.path.join(path, '.gpg-id'), 'r') as gpg_id_file:
        if gpg_id_file.read().strip() == gpg_id:
            add_gpg_id = False

    if add_gpg_id:
        # Create .gpg_id and put the gpg id in it
        with open(os.path.join(path, '.gpg-id'), 'a') as gpg_id_file:
            gpg_id_file.write(gpg_id)

    click.echo("Password store initialized for %s." % gpg_id)


@main.command()
@click.argument('path', type=click.STRING)
@click.pass_obj
def insert(config, path):
    passfile_path = os.path.realpath(
        os.path.join(
            config['password_store_dir'],
            path + '.gpg'
        )
    )

    password = click.prompt(
        'Enter the password',
        type=str,
        confirmation_prompt=True
    )

    gpg = subprocess.Popen(
        [
            'gpg2',
            '-e',
            '-r', config['gpg-id'],
            '--batch',
            '--use-agent',
            '--no-tty',
            '-o', passfile_path
        ],
        shell=False,
        stdin=subprocess.PIPE
    )

    gpg.stdin.write(password.encode())
    gpg.stdin.close()
    gpg.wait()


@main.command()
@click.argument('path', type=click.STRING)
@click.pass_obj
def show(config, path):
    passfile_path = os.path.realpath(
        os.path.join(
            config['password_store_dir'],
            path + '.gpg'
        )
    )

    gpg = subprocess.Popen(
        [
            'gpg2',
            '--quiet',
            '--batch',
            '--use-agent',
            '-d', passfile_path,
        ],
        shell=False,
        stdout=subprocess.PIPE
    )
    gpg.wait()

    if gpg.returncode == 0:
        click.echo(gpg.stdout.read())


@main.command()
@click.argument('subfolder', required=False, type=click.STRING, default='')
@click.pass_obj
def ls(config, subfolder):
    tree = subprocess.Popen(
        [
            'tree',
            '-C',
            '-l',
            '--noreport',
            os.path.join(config['password_store_dir'], subfolder),
        ],
        shell=False,
        stdout=subprocess.PIPE
    )
    tree.wait()

    if tree.returncode == 0:
        output_without_gpg = \
            tree.stdout.read().decode('utf8').replace('.gpg', '')

        output_replaced_first_line =\
            "Password Store\n" + '\n'.join(output_without_gpg.split('\n')[1:])

        output_stripped = output_replaced_first_line.strip()

        click.echo(output_stripped)


@main.command()
@click.argument('search_terms', nargs=-1)
@click.pass_obj
def find(config, search_terms):
    click.echo("Search Terms: " + ','.join(search_terms))

    pattern = '*' + '*|*'.join(search_terms) + '*'

    tree = subprocess.Popen(
        [
            'tree',
            '-C',
            '-l',
            '--noreport',
            '-P', pattern,
            # '--prune', (tree>=1.5)
            # '--matchdirs', (tree>=1.7)
            # '--ignore-case', (tree>=1.7)
            config['password_store_dir'],
        ],
        shell=False,
        stdout=subprocess.PIPE
    )
    tree.wait()

    if tree.returncode == 0:
        output_without_gpg = \
            tree.stdout.read().decode('utf8').replace('.gpg', '')

        output_without_first_line =\
            '\n'.join(output_without_gpg.split('\n')[1:]).strip()

        click.echo(output_without_first_line)


@main.command()
@click.option('--recursive', '-r', is_flag=True)
@click.argument('path', type=click.STRING)
@click.pass_obj
def rm(config, recursive, path):
    resolved_path = os.path.realpath(
        os.path.join(config['password_store_dir'], path)
    )

    if os.path.isdir(resolved_path) is False:
        resolved_path = os.path.join(
            config['password_store_dir'],
            path + '.gpg'
        )

    if os.path.exists(resolved_path):
        if recursive:
            shutil.rmtree(resolved_path)
        else:
            os.remove(resolved_path)
    else:
        click.echo("Error: %s is not in the password store" % path)


@main.command()
@click.argument('old_path', type=click.STRING)
@click.argument('new_path', type=click.STRING)
@click.pass_obj
def mv(config, old_path, new_path):
    resolved_old_path = os.path.realpath(
        os.path.join(config['password_store_dir'], old_path)
    )

    if os.path.isdir(resolved_old_path):
        shutil.move(
            resolved_old_path,
            os.path.realpath(
                os.path.join(config['password_store_dir'], new_path)
            )
        )
    else:
        resolved_old_path = os.path.realpath(
            os.path.join(config['password_store_dir'], old_path + '.gpg')
        )

        if os.path.isfile(resolved_old_path):
            shutil.move(
                resolved_old_path,
                os.path.realpath(
                    os.path.join(
                        config['password_store_dir'],
                        new_path + '.gpg'
                    )
                )
            )
        else:
            click.echo("Error: %s is not in the password store" % old_path)


@main.command()
@click.argument('commands', nargs=-1)
@click.pass_obj
def git(config, commands):
    command_list = list(commands)

    git_result = subprocess.Popen(
        ['git'] + command_list,
        shell=False,
    )
    git_result.wait()

    if len(command_list) > 0 and command_list[0] == 'init':
        git_add_and_commit(
            '.',
            message="Add current contents of password store."
        )

        # Create .gitattributes and commit it
        with open(
                os.path.join(
                    config['password_store_dir'], '.gitattributes'), 'w'
        ) as gitattributes:
            gitattributes.write('*.gpg diff=gpg\n')

        git_add_and_commit(
            '.gitattributes',
            message="Configure git repository for gpg file diff."
        )

        subprocess.Popen(
            ['git', 'config', '--local', 'diff.gpg.binary', 'true'],
            shell=False
        ).wait()

        subprocess.Popen(
            ['git', 'config', '--local', 'diff.gpg.textconv', 'gpg -d'],
            shell=False
        ).wait()

if __name__ == '__main__':
    main()
