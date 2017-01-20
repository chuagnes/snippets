create table snippets (
keyword text primary key,
message text not null default ''
);

--find all keywords
select keyword from snippets;

select * from snippets where keyword = 'delete';

update snippets set message='Insert new rows into a table' where keyword='insert';

delete from snippets where keyword='insert';