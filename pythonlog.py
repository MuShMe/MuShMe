$ python
Python 2.7.3 (default, Apr 10 2013, 06:20:15) 
[GCC 4.6.3] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import mutagen
>>> from mutagen import ID3
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: cannot import name ID3
>>> from mutagen import id3
>>> from mutagen.mp3 import EasyMP3 as MP3
>>> MP3('/mnt/hgfs/Music/Ink.mp3')
{'album': [u'Ghost Stories'], 'performer': [u'Coldplay'], 'copyright': [u'\u2117 2014 Parlophone Records Limited, a Warner Music Group Company.'], 'artist': [u'Coldplay'], 'title': [u'Ink'], 'encodedby': [u'BiebkBohidar'], 'date': [u'2014'], 'tracknumber': [u'3'], 'genre': [u'Rock']}
>>> dict(MP3('/mnt/hgfs/Music/Ink.mp3'))
{'album': [u'Ghost Stories'], 'performer': [u'Coldplay'], 'copyright': [u'\u2117 2014 Parlophone Records Limited, a Warner Music Group Company.'], 'artist': [u'Coldplay'], 'title': [u'Ink'], 'encodedby': [u'BiebkBohidar'], 'date': [u'2014'], 'tracknumber': [u'3'], 'genre': [u'Rock']}
>>> audio=ID3('/mnt/hgfs/Music/Ink.mp3')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'ID3' is not defined
>>> from mutagen.id3 import ID#
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ImportError: cannot import name ID
>>> from mutagen.id3 import ID3
>>> audio=ID3('/mnt/hgfs/Music/Ink.mp3')
>>> print audio

print audio['data']
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "mutagen/_util.py", line 199, in __getitem__
    return self.__dict[key]
KeyError: 'data'
>>> print audio['TIT2']
Ink
>>> print audio['APIC']
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "mutagen/_util.py", line 199, in __getitem__
    return self.__dict[key]
KeyError: 'APIC'
>>> print audio[APIC]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'APIC' is not defined
>>> print audio[]
  File "<stdin>", line 1
    print audio[]
                ^
SyntaxError: invalid syntax
>>> print audio['mime']
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "mutagen/_util.py", line 199, in __getitem__
    return self.__dict[key]
KeyError: 'mime'
>>> audio.tags['APIC:'].data
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'ID3' object has no attribute 'tags'
>>> file = FILE('/mnt/hgfs/Music/Ink.mp3')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'FILE' is not defined
>>> from mutagen import File
>>> file = File('/mnt/hgfs/Music/Ink.mp3')
>>> file.tags['APIC:'].data

