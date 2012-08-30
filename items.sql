/*
 Navicat PostgreSQL Data Transfer

 Source Server         : ikea app

 Target Server Version : 90105
 File Encoding         : utf-8

*/

-- ----------------------------
--  Table structure for "items"
-- ----------------------------
DROP TABLE IF EXISTS "items";
CREATE TABLE "items" (
	"user_id" int4 NOT NULL,
	"product" varchar(2000),
	"loc" varchar(5000),
	"price" varchar(2000),
	"url" varchar(2000),
	"id" int4 NOT NULL DEFAULT nextval('items_id_seq'::regclass)
)


-- ----------------------------
--  Primary key structure for table "items"
-- ----------------------------
ALTER TABLE "items" ADD CONSTRAINT "items_pkey" PRIMARY KEY ("id") NOT DEFERRABLE INITIALLY IMMEDIATE;

