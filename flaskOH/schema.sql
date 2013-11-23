drop table if exists entries;
create table entries (
    id integer primary key autoincrement,
    name text not null,
    description text not null,
    category text not null
);
