drop table if exists movies;
create table movies (
    movieID integer primary key autoincrement unique,
    title text not null
);