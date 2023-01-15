import os
import pathlib
import unittest

from sqlmin import SQLMinifier


CONTAINING_DIR = pathlib.Path(__file__).parent.resolve()


class SqlMinifierTestCase(unittest.TestCase):

    def setUp(self):
        self.minifier = SQLMinifier()
    
    def minify(self, sql):
        return self.minifier.minify(sql)
    
    def open(self, path, *args, **kwargs):
        with open(os.path.join(CONTAINING_DIR, path), *args, **kwargs) as fd:
            return fd.read()

    def test_minified_sql_gives_same_result(self):
        sql = "SELECT * FROM schema.mytable;"

        assert self.minify(sql) == sql

    def test_removes_newline(self):
        sql = "SELECT * FROM\nschema.mytable\nWHERE column = 'value'\n;"
        expected = "SELECT * FROM schema.mytable WHERE column = 'value';"

        assert self.minify(sql) == expected

    def test_removes_multiple_spaces(self):
        sql = "SELECT  *  FROM\nschema.mytable;"
        expected = "SELECT * FROM schema.mytable;"

        assert self.minify(sql) == expected

    def test_removes_single_line_comments(self):
        sql = "SELECT  *  FROM -- This is a comment\nschema.mytable; --This should be removed"
        expected = "SELECT * FROM schema.mytable;"

        assert self.minify(sql) == expected

    def test_removes_multi_line_comments(self):
        sql = "/*\nThis\nis\na\nmulti-line\ncomment\n*/\nSELECT  *  FROM \nschema.mytable; /* This should be removed. */"
        expected = "SELECT * FROM schema.mytable;"

        assert self.minify(sql) == expected

    def test_removes_spaces_between_semicolon(self):
        sql = """SELECT * FROM schema.mytable WHERE column = 'value'    ;   CREATE TABLE schema.myothertable;"""
        expected = "SELECT * FROM schema.mytable WHERE column = 'value';CREATE TABLE schema.myothertable;"

        assert self.minify(sql) == expected

    def test_removes_spaces_between_commas(self):
        sql = """SELECT var1, var2, var3, var4 FROM schema.mytable WHERE column = 'value';"""
        expected = "SELECT var1,var2,var3,var4 FROM schema.mytable WHERE column = 'value';"

        assert self.minify(sql) == expected

    def test_removes_space_between_left_parenthesis(self):
        sql = """( SELECT * FROM schema.mytable WHERE column = 'value');"""
        expected = "(SELECT * FROM schema.mytable WHERE column = 'value');"

        assert self.minify(sql) == expected

    def test_removes_space_between_right_parenthesis(self):
        sql = """(SELECT * FROM schema.mytable WHERE column = 'value' );"""
        expected = "(SELECT * FROM schema.mytable WHERE column = 'value');"

        assert self.minify(sql) == expected

    def test_integration_1(self):
        sql = self.open("sql/1.sql")
        expected = "DROP TABLE IF EXISTS temp_location_holds_counts;CREATE TEMP TABLE temp_location_holds_counts AS SELECT t.bib_record_id,count(t.bib_record_id)as count_holds_on_title FROM(SELECT CASE WHEN r.record_type_code = 'i' THEN(SELECT l.bib_record_id FROM sierra_view.bib_record_item_record_link as l WHERE l.item_record_id = h.record_id LIMIT 1)WHEN r.record_type_code = 'b' THEN h.record_id ELSE NULL END AS bib_record_id FROM sierra_view.hold as h JOIN sierra_view.record_metadata as r ON r.id = h.record_id)AS t GROUP BY t.bib_record_id HAVING count(t.bib_record_id)> 1 ORDER BY count_holds_on_title;CREATE INDEX temp_hold_data_bib_record_id ON temp_location_holds_counts(bib_record_id);ANALYZE temp_location_holds_counts;SELECT ROW_NUMBER()OVER(ORDER BY t.count_holds_on_title DESC)AS field_booklist_entry_rank,'http://find.minlib.net/iii/encore/record/C__R'||id2reckey(t.bib_record_id)AS \"field_booklist_entry_encore_url\",best_title AS title,REPLACE(SPLIT_PART(SPLIT_PART(b.best_author,'(',1),',',2),'.','')||' '||SPLIT_PART(b.best_author,',',1)AS field_booklist_entry_author,(SELECT 'https://syndetics.com/index.aspx?isbn='||SUBSTRING(s.content FROM '[0-9]+')||'/SC.gif&client=minuteman' FROM sierra_view.subfield s WHERE b.bib_record_id = s.record_id AND s.marc_tag = '020' AND s.tag = 'a' ORDER BY s.occ_num LIMIT 1)AS field_booklist_entry_cover FROM temp_location_holds_counts t JOIN sierra_view.bib_record_property b ON t.bib_record_id = b.bib_record_id and b.material_code = 'a' AND b.best_title NOT LIKE '%Non-MLN%' GROUP BY 2,3,4,5,t.count_holds_on_title ORDER BY t.count_holds_on_title DESC LIMIT 50;"

        assert self.minify(sql) == expected

    def test_integration_2(self):
        sql = self.open("sql/2.sql")
        expected = "(SELECT * FROM(SELECT DISTINCT 'https://find.minlib.net/iii/encore/record/C__R'||id2reckey(b.bib_record_id)AS field_booklist_entry_encore_url,b.best_title AS title,REPLACE(SPLIT_PART(SPLIT_PART(b.best_author,'(',1),',',2),'.','')||' '||SPLIT_PART(b.best_author,',',1)AS field_booklist_entry_author,(SELECT 'https://syndetics.com/index.aspx?isbn='||SUBSTRING(s.content FROM '[0-9]+')||'/SC.gif&client=minuteman' FROM sierra_view.subfield s WHERE b.bib_record_id = s.record_id AND s.marc_tag = '020' AND s.tag = 'a' ORDER BY s.occ_num LIMIT 1)AS field_booklist_entry_cover FROM sierra_view.bib_record_property b JOIN sierra_view.bib_record_item_record_link l ON b.bib_record_id = l.bib_record_id JOIN sierra_view.item_record i ON l.item_record_id = i.id AND i.is_available_at_library = 'TRUE' AND i.item_status_code NOT IN('m','n','z','t','o','$','!','w','d','p','r','e','j','u','q','x','y','v')AND SUBSTRING(i.location_code,4,1)IN('j','y')JOIN sierra_view.phrase_entry d ON b.bib_record_id = d.record_id AND d.varfield_type_code = 'd' AND REPLACE(d.index_entry,' ','')LIKE '%christmas%' AND(REPLACE(d.index_entry,' ','')LIKE '%decorations%' OR REPLACE(d.index_entry,' ','')LIKE '%history%' OR REPLACE(d.index_entry,' ','')LIKE '%cook%')WHERE b.material_code = 'a' AND b.publish_year >= '2000' GROUP BY 1,2,3,4)a ORDER BY RANDOM()LIMIT 25)UNION(SELECT * FROM(SELECT DISTINCT 'https://find.minlib.net/iii/encore/record/C__R'||id2reckey(b.bib_record_id)AS field_booklist_entry_encore_url,b.best_title AS title,REPLACE(SPLIT_PART(SPLIT_PART(b.best_author,'(',1),',',2),'.','')||' '||SPLIT_PART(b.best_author,',',1)AS field_booklist_entry_author,(SELECT 'https://syndetics.com/index.aspx?isbn='||SUBSTRING(s.content FROM '[0-9]+')||'/SC.gif&client=minuteman' FROM sierra_view.subfield s WHERE b.bib_record_id = s.record_id AND s.marc_tag = '020' AND s.tag = 'a' ORDER BY s.occ_num LIMIT 1)AS field_booklist_entry_cover FROM sierra_view.bib_record_property b JOIN sierra_view.bib_record_item_record_link l ON b.bib_record_id = l.bib_record_id JOIN sierra_view.item_record i ON l.item_record_id = i.id AND i.is_available_at_library = 'TRUE' AND i.item_status_code NOT IN('m','n','z','t','o','$','!','w','d','p','r','e','j','u','q','x','y','v')AND SUBSTRING(i.location_code,4,1)IN('j','y')JOIN sierra_view.phrase_entry d ON b.bib_record_id = d.record_id AND d.varfield_type_code = 'd' AND REPLACE(d.index_entry,' ','')LIKE '%hanukkah%' AND REPLACE(d.index_entry,' ','')LIKE '%juvenileliterature%' WHERE b.material_code = 'a' AND b.publish_year >= '2000' GROUP BY 1,2,3,4)b ORDER BY RANDOM()LIMIT 15)UNION(SELECT * FROM(SELECT DISTINCT 'https://find.minlib.net/iii/encore/record/C__R'||id2reckey(b.bib_record_id)AS field_booklist_entry_encore_url,b.best_title AS title,REPLACE(SPLIT_PART(SPLIT_PART(b.best_author,'(',1),',',2),'.','')||' '||SPLIT_PART(b.best_author,',',1)AS field_booklist_entry_author,(SELECT 'https://syndetics.com/index.aspx?isbn='||SUBSTRING(s.content FROM '[0-9]+')||'/SC.gif&client=minuteman' FROM sierra_view.subfield s WHERE b.bib_record_id = s.record_id AND s.marc_tag = '020' AND s.tag = 'a' ORDER BY s.occ_num LIMIT 1)AS field_booklist_entry_cover FROM sierra_view.bib_record_property b JOIN sierra_view.bib_record_item_record_link l ON b.bib_record_id = l.bib_record_id JOIN sierra_view.item_record i ON l.item_record_id = i.id AND i.is_available_at_library = 'TRUE' AND i.item_status_code NOT IN('m','n','z','t','o','$','!','w','d','p','r','e','j','u','q','x','y','v')AND SUBSTRING(i.location_code,4,1)IN('j','y')JOIN sierra_view.phrase_entry d ON b.bib_record_id = d.record_id AND d.varfield_type_code = 'd' AND REPLACE(d.index_entry,' ','')LIKE '%kwanza%' WHERE b.material_code = 'a' AND b.publish_year >= '2000' GROUP BY 1,2,3,4)c ORDER BY RANDOM()LIMIT 10)"

        assert self.minify(sql) == expected

    def test_minified_integration_1_gives_same_result(self):
        sql = self.open("sql/1.sql")

        assert self.minify(self.minify(sql)) == self.minify(sql)

    def test_minified_integration_2_gives_same_result(self):
        sql = self.open("sql/2.sql")

        assert self.minify(self.minify(sql)) == self.minify(sql)
