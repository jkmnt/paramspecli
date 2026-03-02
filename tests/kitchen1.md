# myprog

**My Program**

Options:

- `--help`, `-h`

    Show help and exit

Commands:

- [net ...](#myprog-net)

## myprog net ...

Net stuff

Aliases:

- **network**

Options:

- `--help`, `-h`

    Show help and exit

Commands:

some commands ...

- [serve](#myprog-net-serve)

- [dummy ...](#myprog-net-dummy)

- [nop](#myprog-net-nop)

### myprog net serve

**My Command**

Usage:

```
myprog net serve [options] [net options] IP [IP ...]
```

Arguments:

Fugazi

- `IP`

    IP address

    Possible values:

    - `127.0.0.1`
    - `0.0.0.0`

Options:

- `--help`, `-h`

    Show help and exit

- `--debug`/`--no-debug`, `-g`

    Enable debug (default: `--no-debug`)

- `--some3` *SOME3*

    Unsure#3 ... (default: `42`)

Net options:

Popular network options

- `--port`, `-p` *PORT \[PORT ...\]*

    Port to use

    Possible values:

    - `80`: production
    - `8080`: internal

- `--some` *SOME*

    Unsure ... (default: `:-)`)

- `--some2` *SOME2*

    Unsure#2 ... (default: `who knows`)

### myprog net dummy ...

Does nothing

Options:

- `--help`, `-h`

    Show help and exit

### myprog net nop

It nops!

Usage:

```
myprog net nop [options]
```

Options:

- `--help`, `-h`

    Show help and exit

