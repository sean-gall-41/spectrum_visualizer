# Spectrum Visualizer
This program visualizes the frequencies of an input sound file if provided, otherwise it generates a sine wave of a specified frequency and duration.

## Usage
Usage note 1: running the program without any parameters generates a sine 
              wave with frequency 440Hz and duration 1s.

Usage note 2: The FILE parameter is meant to be mutually exclusive to both 
              the FREQUENCY and DURATION parameters. Argparse doesn't have
              this kind of feature (as far as I know of, outside of 
              subcommands) so it will not check for this. So if you include
              the FILE parameter, the program will ignore the FREQUENCY and
              DURATION parameters, and will generate and error if any other
              type of input is encountered. 
```
usage: audio_visualizer.py [-h] [-f FILE] [-fr FREQUENCY] [-d DURATION]

    -h, --help          displays a message with the information here
    -f FILE, --file     FILE include the file to be analyzed and played
                        Accepted formats are: *.wav
    -fr FREQUENCY, --frequency
                        frequency (in Hz) of generated sine wave
                        (default 440.)
    -d DURATION, --duration DURATION
                        duration (in seconds) of the generated sine wave
                        (default 1.0)
```

## Examples
```
python audio_visualizer.py -f my_favorite_song.wav
python audio_visualizer.py -fr 100. -d 2.5
python audio_visualizer.py
```

## Notes
(02/10/2020)
    - Not all input cases have been thoroughly tested. You've been warned :)
    - I have not tested the program on other platforms besides Windows 10, so 
      I am not sure how it will behave when run on other platforms.

## Bugs
    - input validation (including reasonable values of FREQUENCY and DURATION)
