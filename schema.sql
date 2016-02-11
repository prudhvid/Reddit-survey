create table user(
   roll text primary key,
   name text);
 create table survey(
   user text,
   subreddit text,
   value integer);