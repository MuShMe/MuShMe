
PARTICULAR TABLES :

drop table if exists entries;
CREATE TABLE entries (
User_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
Username VARCHAR(100) NOT NULL,
Email_id VARCHAR(120) NOT NULL UNIQUE,
Pwdhash VARCHAR(100) NOT NULL,
Privilege INT NOT NULL,
Profile_pic BLOB NOT NULL,														-----
Name VARCHAR(100) NOT NULL,
DOB	date ,
Last_login date
);

drop table if exists songs;
CREATE TABLE songs (
Song_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
Song_title VARCHAR(100) NOT NULL,
Genre VARCHAR(100),
Song_type VARCHAR(100),
Rating INT,
Length VARCHAR(100) NOT NULL,
Country VARCHAR(100) NOT NULL,
Song_year INT,
Uploaded_when DATETIME NOT NULL
);

drop table if exists albums;
CREATE TABLE albums (
Album_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
Album_pic              																-----
Album_name VARCHAR(100) NOT NULL,
Album_year INT,
No_of_tracks INT,
Total_length TIME NOT NULL,
Publisher VARCHAR(100) NOT NULL,
);

drop table if exists artists;
CREATE TABLE artists (
Artist_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
Country VARCHAR(100),
Begin_date_year INT,
Artist_pic
Artist_name VARCHAR(100) NOT NULL,
End_date_year INT,
Last_updated DATETIME NOT NULL;
);

drop table if exists playlists;
CREATE TABLE playlists (
Playlist_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
Playlist_name VARCHAR(100) NOT NULL,
Favourite INT NOT NULL
);

drop table if exists comments;
CREATE TABLE comments (
Comment_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
Comment VARCHAR(5000) NOT NULL,
Flag_on_comment INT,
User_id INT NOT NULL,
foreign key(User_id) references entries(User_id)
ON UPDATE CASCADE ON DELETE CASCADE
);


drop table if exists complains;
CREATE TABLE complains (
Complain_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
Complain_type INT,
Complain_description VARCHAR(100) NOT NULL,
Action_by_admin VARCHAR(100) NOT NULL,
Comment_id INT NOT NULL,
foreign key(Comment_id) references comments(Comment_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists requests;
CREATE TABLE requests (
Request_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
Request_from INT NOT NULL,
Request_to INT NOT NULL,
Status INT NOT NULL,
Date_of_sending DATE NOT NULL,
foreign key(Request_to) references entries(User_id),
foreign key(Request_from) references entries(User_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists recommend;
CREATE TABLE recommend (
Recommend_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
User_id_from INT NOT NULL,
User_id_to INT NOT NULL,
Date_recommend DATE NOT NULL,
foreign key(User_id_to) references entries(User_id),
foreign key(User_id_from) references entries(User_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

RELATIONSHIP TABLES :

drop table if exists friends;
CREATE TABLE friends (
User_id1 INT NOT NULL,
User_id2 INT NOT NULL,
foreign key(User_id1) references entries(User_id),
foreign key(User_id2) references entries(User_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists user_playlist;
CREATE TABLE user_playlist (
Playlist_id INT NOT NULL,
User_id INT NOT NULL,
foreign key(User_id) references entries(User_id),
foreign key(Playlist_id) references playlists(Playlist_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists user_song;
CREATE TABLE user_song (
User_id INT NOT NULL,
Song_id INT NOT NULL,
foreign key(Song_id) references songs(Song_id),
foreign key(User_id) references entries(User_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists album_songs;
CREATE TABLE album_songs (
Album_id INT NOT NULL,
Song_id INT NOT NULL,
foreign key(Song_id) references songs(Song_id),
foreign key(Album_id) references albums(Album_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists album_artists;
CREATE TABLE album_artists (
Album_id INT NOT NULL,
Artist_id INT NOT NULL,
foreign key(Artist_id) references artists(Artist_id),
foreign key(Album_id) references albums(Album_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists song_artists;
CREATE TABLE song_artists (
Song_id INT NOT NULL,
Artist_id INT NOT NULL,
foreign key(Artist_id) references artists(Artist_id),
foreign key(Song_id) references songs(Song_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists playlist_comments;
CREATE TABLE palylist_comments (
Playlist_id INT NOT NULL,
Comment_id INT NOT NULL,
foreign key(Playlist_id) references playlists(Playlist_id),
foreign key(Comment_id) references comments(Comment_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists song_comments;
CREATE TABLE song_comments (
Song_id INT NOT NULL,
Comment_id INT NOT NULL,
foreign key(Song_id) references songs(Song_id),
foreign key(Comment_id) references comments(Comment_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists user_like_comments;
CREATE TABLE user_like_comments (
User_id INT NOT NULL,
Comment_id INT NOT NULL,
foreign key(User_id) references entries(User_id),
foreign key(Comment_id) references comments(Comment_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists user_complains;
CREATE TABLE user_complains (
User_id INT NOT NULL,
Complain_id INT NOT NULL,
foreign key(User_id) references entries(User_id),
foreign key(Complain_id) references complains(Complain_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists recommend_playlists;
CREATE TABLE recommend_playlists (
Playlist_id INT NOT NULL,
Recommend_id INT NOT NULL,
foreign key(Playlist_id) references playlists(Playlist_id),
foreign key(Recommend_id) references recommend(Recommend_id)
ON UPDATE CASCADE ON DELETE CASCADE
);

drop table if exists recommend_songs;
CREATE TABLE recommend_songs (
Song_id INT NOT NULL,
Recommend_id INT NOT NULL,
foreign key(Song_id) references songs(Song_id),
foreign key(Recommend_id) references recommend(Recommend_id)
ON UPDATE CASCADE ON DELETE CASCADE
);
