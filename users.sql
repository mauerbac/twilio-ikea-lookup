/*
 Navicat PostgreSQL Data Transfer

 Source Server         : ikea app
 Source Server Version : 90105

 Source Schema         : public

 File Encoding         : utf-8

*/

-- ----------------------------
--  Table structure for "users"
-- ----------------------------
DROP TABLE IF EXISTS "users";
CREATE TABLE "users" (
	"userid" int4 NOT NULL DEFAULT nextval('users4_userid_seq'::regclass),
	"numbers" varchar(60) NOT NULL
)

-- ----------------------------
--  Primary key structure for table "users"
-- ----------------------------
ALTER TABLE "users" ADD CONSTRAINT "users_pkey1" PRIMARY KEY ("numbers") NOT DEFERRABLE INITIALLY IMMEDIATE;

