-- 0 is boy 1 is girl

drop table if exists chats;

create table chats (
       id integer primary key autoincrement,
       chatopen integer,
       personaid text,
       personbid text,
       gendera integer,
       genderb integer,
       disconnected integer
);
