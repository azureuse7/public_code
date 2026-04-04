# What Is /dev/null

**Reference:** [Linux Hint - What is /dev/null](https://linuxhint.com/what_is_dev_null/)

Linux treats everything as a file. The `/dev` directory is used to store all the physical and virtual devices. If you have worked with disk partitioning, you may have seen the `/dev` directory in use — for example, `/dev/sda`, `/dev/sdb1`, etc.

Some of the popular virtual devices include:

```
/dev/null
/dev/zero
/dev/random
/dev/urandom
```

The `/dev/null` is a null device that discards any data written to it. However, it reports back that the write operation was successful. In UNIX terminology, this null device is also referred to as the "bit bucket" or "black hole."

Despite its unique features, `/dev/null` is a valid file. You can verify it using the following command:

```bash
stat /dev/null
```

## Basic Usage

Anything written to `/dev/null` vanishes permanently. The following example demonstrates this property:

```bash
echo "hello world" > /dev/null
cat /dev/null
```

Here, we redirect the STDOUT of the `echo` command to `/dev/null`. Using the `cat` command, we read the content of `/dev/null`. Since `/dev/null` does not store any data, there is nothing in the output of the `cat` command.

To use `/dev/null` effectively, you need to understand file descriptors: `STDIN`, `STDOUT`, and `STDERR`.

## Examples

### Example 1: Redirect STDOUT

```bash
echo "hello world" > /dev/null
```

Here, we redirect the STDOUT of the `echo` command to `/dev/null`. That is why it produces no output in the console.

### Example 2: Redirect STDERR

```bash
asdfghjkl > /dev/null
```

Here, `asdfghjkl` is a command that does not exist, so Bash produces an error. However, the error message does not get flushed to `/dev/null` because the error message is stored in STDERR. To discard the error message, specify the STDERR (`2`) redirection as well:

```bash
asdfghjkl 2> /dev/null
```

### Example 3: Redirect Both STDOUT and STDERR

To redirect both STDOUT and STDERR to `/dev/null`, you could use this structure:

```bash
<command> > /dev/null 2> /dev/null
```

While this is completely valid, it is verbose and redundant. A shorter way is to redirect STDERR to STDOUT first, then redirect STDOUT to `/dev/null`:

```bash
<command> > /dev/null 2>&1
```

Here, STDOUT is redirected to `/dev/null`. Then, STDERR (`2`) is redirected to STDOUT (`1`). The `&1` tells the shell that the destination is a file descriptor, not a file name.
