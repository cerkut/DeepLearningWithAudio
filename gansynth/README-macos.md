# GANSynth setup (macOS)

## Prerequisites

You should have [Purr Data](https://agraef.github.io/purr-data/) installed. Pd vanilla may work too, but the setup will be slightly different and we have not tested it.

If you've never used the command line before, it may be a good idea to have a look at a [tutorial](https://macpaw.com/how-to/use-terminal-on-mac) first to learn some of the basics.

## Install Xcode command line tools

Apple's Xcode command line developer tools are required for setup. If you have the regular Xcode installed from App Store, the command line tools should already be included.

To install the command line tools, open Terminal and run:

```
$ xcode-select --install
```

This will pop up a dialog to guide you through the installation.

## Clone the course repository

If you don't already have this repository on your computer, clone it:

```
$ git clone https://github.com/SopiMlab/DeepLearningWithAudio2019.git
```

This will download the repository into your current working directory, which in a new terminal window is your home directory.

## Install Conda

Install Miniconda, following the [official instructions](https://conda.io/projects/conda/en/latest/user-guide/install/macos.html).

Note that if you're using a shell other than the default Bash, the Miniconda installer will probably not set up your environment correctly. If you're not sure, you can check your shell with:

```
$ echo $SHELL
```

If this reports something other than `/bin/bash`, you can revert to Bash by running

```
$ chsh -s /bin/bash
```

and opening a new terminal window.

## Download Magenta

Enter the root directory of the course repository. For example, if you cloned it into your home directory:

```
$ cd ~/DeepLearningWithAudio2019
```

Clone our Magenta repository:

```
$ git clone https://github.com/SopiMlab/magenta.git
```

## Install Magenta

There are two variants of Magenta, `magenta` (runs on CPU) and `magenta-gpu` (runs on GPU). We will use the CPU variant, as it has the widest hardware compatibility. In case you have an NVIDIA graphics card, `magenta-gpu` can provide a substantial performance boost, however it is also a bit trickier to set up.

Enter the previously created Magenta directory:

```
$ cd magenta
```

Create a Conda environment (named "magenta" here):

```
$ conda create -n magenta python=2.7 libopenblas=0.3
```

This will ask you for confirmation, create a Python 2.7 environment and install some packages.

Activate the environment:

```
$ conda activate magenta
```

This should update your command line prompt to say `(magenta)` at the start.

Note that activating the Conda environment only applies to your current terminal window! If you open a  new window, you'll have to run this command again.

Install Magenta into the Conda environment from the current directory using pip, Python's package manager:

```
$ pip install .
``` 

During the installation, you may see some errors about packages like `googledatastore` and `apache-beam`. These can be ignored.

You should now see Magenta in the output of `pip list`:

```
$ pip list

Package                            Version
---------------------------------- -----------
...
magenta                            1.1.2
...
```

## Download GANSynth checkpoint

Enter the `gansynth` directory:

```
$ cd ../gansynth
```

Google provides two [pre-trained neural networks](https://github.com/tensorflow/magenta/tree/master/magenta/models/gansynth#generation), called checkpoints. In this example, we will use `all_instruments`, which is trained on all instruments in the NSynth dataset. There is also `acoustic_only`, trained on the acoustic instruments only. Feel free to experiment with both!

To download the `all_instruments` checkpoint, run:

```
$ curl -LO https://storage.googleapis.com/magentadata/models/gansynth/all_instruments.zip
```

Extract the zip:

```
$ unzip all_instruments.zip
```

Feel free to remove the zip file at this point.

## Verify that GANSynth is working

Generate some random notes:

```
$ gansynth_generate --ckpt_dir=all_instruments --output_dir=output
```

This will print a bunch of warnings, but should eventually produce a few wav files in the `output` subdirectory.

## Build pyext

Enter the `pyext-setup` directory:

```
$ cd ../pyext-setup
```

Run the `build.py` script with the `--info` flag to check your environment:

```
$ python build.py --info

Python version: 2.7.16 |Anaconda, Inc.| (default, Aug 19 2019, 18:51:18) 
[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]
Python executable: /Users/miranda/miniconda3/envs/magenta/bin/python
Pd path: /Applications/Pd-l2ork.app
Pd variant: Purr Data
Conda root: /Users/miranda/miniconda3/envs/magenta
```

The output on your system will differ a bit according to your corresponding paths.

If the script fails to find your Pd path, or finds the wrong version, you can specify it manually with the `--pd` option:

```
$ python build.py --info --pd /Users/miranda/SomeUnusualPdFolder/Pd-l2ork.app

Python version: 2.7.16 |Anaconda, Inc.| (default, Aug 19 2019, 18:51:18) 
[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]
Python executable: /Users/miranda/miniconda3/envs/magenta/bin/python
Pd path: /Users/miranda/SomeUnusualPdFolder/Pd-l2ork.app
Pd variant: Purr Data
Conda root: /Users/miranda/miniconda3/envs/magenta
```

Now build pyext by running the same command without `--info` (keep the `--pd` option if you needed to add it before):

```
$ python build.py
```

This creates a binary called `py.pd_darwin` in the `build/py` subdirectory. It is normal for some warnings to appear during the build.

## Install pyext

Create a directory in your Library for Purr Data externals:

```
$ mkdir -p ~/Library/Pd-l2ork
```

(In case the directory already exists, this command will do nothing, so it's safe to run either way.)

Move `py.pd_darwin` into the newly created directory:

```
$ mv build/py/py.pd_darwin ~/Library/Pd-l2ork/
```

Start Purr Data. Go to Edit → Preferences → Startup and add `py` to the libraries list:

![uhh](README-media/purr_data_add_py.png)

Save the preferences by clicking Ok and restart Purr Data. There should be a message about pyext in the main window, e.g.:

```
------------------------------------------------
py/pyext 0.2.2 - python script objects
(C)2002-2015 Thomas Grill - http://grrrr.org/ext

using Python 2.7.16 |Anaconda, Inc.| (default, Aug 19 2019, 18:51:18) 
[GCC 4.2.1 Compatible Clang 4.0.1 (tags/RELEASE_401/final)]

Python array support enabled
------------------------------------------------
```

Congratulations, you've got it working!

You should now be able to open `gansynth.pd` in Purr Data. It will take a moment to load, during which the program may appear to be idle.