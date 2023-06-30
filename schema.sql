drop table if exists movies;
create table movies (
    movieID integer primary key autoincrement unique,
    title text not null,
    description text,
    imdbRating integer,
    rtCriticRating integer,
    rtAudienceRating integer,
    metaRating integer
);

INSERT INTO movies (title, description, imdbRating, rtCriticRating, rtAudienceRating, metaRating) VALUES ("Inception",
"A group of people try to plant an idea in someones head through their dreams", "8.8", "8.7", "9.1", "7.4");

INSERT INTO movies (title, description, imdbRating, rtCriticRating, rtAudienceRating, metaRating) VALUES (
"Grosse Pointe Blank", "A professional hitman attends his high school reunion", "7.3", "7.6", "8.2", "8.7");