https://youngstone89.medium.com/setting-up-environment-variables-in-mac-os-28e5941c771c

1. Check the current environment variable settings.
you can list up by command “printenv” in the console.



if you want to check a specific environment variable, you can do check it with command “echo $variable_name”



PATH variable setting
2. Set an Environment Variable — temporary or permanent
you can set an environment variable for the temporary or permanent use. It depends on the case, if you need a variable for just one time, you can set it up using terminal. Otherwise, you can have it permanently in Bash Shell Startup Script with “Export” command.

Temporary Setting


Set a temporary environment variable using export command
And then close the terminal window and open another one to check out if the set variable has disappeared or not.


Temporary Variable is gone now.
2) Permanent Setting

For permanent setting, you need to understand where to put the “export” script. Here in this practice, you are going to edit “.bash_profile” file under your home directory.

Open the file with your preferred editor like


here “~/” path points to your home directory, don’t get confused about it.

For experiment, I am going to add a test directory to the PATH environment variable. Using “export” command, the PATH variable is going to hold the newly added directory.



Editing .bash_profile file with nano editor.
Make sure to execute this to reload


Be sure to reload the profile config again.

Once refresh environment variable with “source” command, the current shell can locate the new directory for executable binary files.

the PATH variable now holds the newly added value

After removing export line in .bash_profile, then source it, and reopen the terminal.

it’s gone now.
In the end, I have successfully practiced permanent setting. This is going to be useful for any development environment setting hereafter.

Thanks!