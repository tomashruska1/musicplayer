# musicplayer

An old school ligth-weight mp3 player written in python3 using the wrapper around the Qt5 library PyQt5.

## Functions

Has a separate tab for all artists, albums and user-created playlists in the library as well as a dedicated view for the currently played list of songs.

Has a panel diplaying songs for the currently selected artist/album/playlist. From here user can either double click to start playback of the songs displayed on the panel starting from the double-clicked one, right-click to bring up a context menu to add to currently playing, a new or an existing playlist etc.

The songs in the right-hand side panel can be sorted by album name/year for artist view, or artist/album/year for playlist view, either in ascending or descending order.

The right-hand side panel can be resized.

The player has a custom frame with fully implemented behaviour.

User may add one or more folders, these will be scanned for mp3 songs, which will be added into the library, the player will periodically scan the folders to make sure these are up-to-date.

![image](https://user-images.githubusercontent.com/82532992/116453863-a2b40b80-a85f-11eb-9827-1c644e008467.png)
![image](https://user-images.githubusercontent.com/82532992/116454454-4c939800-a860-11eb-9de0-cd76f567777d.png)
![image](https://user-images.githubusercontent.com/82532992/116454508-59b08700-a860-11eb-938a-743d04b53d9c.png)
![image](https://user-images.githubusercontent.com/82532992/116454533-61702b80-a860-11eb-948f-20a5561f9915.png)


## Dependencies

PyQt5, mutagen


## Future plans

Add support for additional formats.
Custom pictures for artists/albums/playlists.
Customizable look
