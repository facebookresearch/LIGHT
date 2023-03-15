# MultiLIGHT

The main teachers for the MultiLIGHT dataset.

## All Characters Teacher
This includes the utterance for all the characters.
```
light dd -t light:multilight:AllCharactersTeacher
```
This teacher generates examples for two of the main tasks in the paper:
* *speaker AND utterance* by setting `--include-speaker-in-label true`, which is the default
* *utterance only* by setting `--include-speaker-in-label false`.

## Single Character Tecahers
```
# replace <SPK> with speaker1, speaker2, or speaker3
light dd -t light:multilight:<SPK>
```
There are a total of three teachers.
Set `--silence-token-dropout` to a flot number in [0, 1] for probablity of discarding silence turns for each of the speakers.

## Speaker Generation Tecaher
Generates the speaker name for the current turn.
```
light dd -t light:multilight:Speaker
```
Setting `--add-current-turn true` will add the utterance from that turn to the context.