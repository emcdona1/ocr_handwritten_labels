
DROP PROCEDURE IF EXISTS SP_AddTag;
DROP PROCEDURE IF EXISTS SP_UpdateTag;
DROP PROCEDURE IF EXISTS SP_DeleteTag;
DROP PROCEDURE IF EXISTS SP_GetTagList;
DROP PROCEDURE IF EXISTS SP_GetTagDetail;

DELIMITER $$

 CREATE PROCEDURE SP_AddTag(
	IN importReference VARCHAR (32),
    IN tagName VARCHAR(255),
    IN originalImagePath VARCHAR(255),
    IN img LONGBLOB,
    IN wordsInfoAsXML LONGTEXT
 )
 BEGIN
	INSERT INTO Tag_Info(
		ImportReference,
		TagName,
		OriginalImagePath)
	VALUES (
		importReference,
		TagName,
		OriginalImagePath);
	SELECT LAST_INSERT_ID() INTO @newTagId;
    
    INSERT INTO Tag_Image(
		TagId,
        Img
    )
    VALUES(
		@newTagId,
        UNHEX(Img)
    );
    
	SET @COUNT = (SELECT EXTRACTVALUE(wordsInfoAsXML,'COUNT(//words/word)'));
    SET @I = 1;
    WHILE(@I <= @COUNT) DO

        INSERT INTO Tag_Word(TagId,OCRDescription,Replacement,Suggestions,Vertices,Category)
        SELECT  @newTagId,
				ExtractValue(wordsInfoAsXML,CONCAT('/words/word[',@I,']/description')),
                ExtractValue(wordsInfoAsXML,CONCAT('/words/word[',@I,']/replacement')),
                ExtractValue(wordsInfoAsXML,CONCAT('/words/word[',@I,']/suggestions')),
                ExtractValue(wordsInfoAsXML,CONCAT('/words/word[',@I,']/vertices')),
                ExtractValue(wordsInfoAsXML,CONCAT('/words/word[',@I,']/category'));
        SET @I = @I + 1;
  
    END WHILE;
    SELECT @newTagId;
 END $$ 
 
 DELIMITER $$
 CREATE PROCEDURE SP_UpdateTag(
	IN tagIdUpdate BIGINT,
    IN wordsInfoAsXML LONGTEXT
 )
 BEGIN
	SELECT tagIdUpdate into @updateTagId;
	DELETE FROM Tag_Word WHERE TagId=@updateTagId;
    SET @COUNT = (SELECT EXTRACTVALUE(wordsInfoAsXML,'COUNT(//words/word)'));
    SET @I = 1;
    WHILE(@I <= @COUNT) DO
        INSERT INTO Tag_Word(TagId,OCRDescription,Replacement,Suggestions,Vertices,Category)
        SELECT  @updateTagId,
				ExtractValue(wordsInfoAsXML,CONCAT('/words/word[',@I,']/description')),
                ExtractValue(wordsInfoAsXML,CONCAT('/words/word[',@I,']/replacement')),
                ExtractValue(wordsInfoAsXML,CONCAT('/words/word[',@I,']/suggestions')),
                ExtractValue(wordsInfoAsXML,CONCAT('/words/word[',@I,']/vertices')),
                ExtractValue(wordsInfoAsXML,CONCAT('/words/word[',@I,']/category'));
        SET @I = @I + 1;
  
    END WHILE;
 END $$
 
DELIMITER $$
 CREATE PROCEDURE SP_DeleteTag(
	IN tagIdDelete BIGINT
 )
 BEGIN
	DELETE FROM Tag_Word WHERE TagId=tagIdDelete;
    DELETE FROM Tag_Image WHERE TagId=tagIdDelete;
    DELETE FROM Tag_Info WHERE TagId=tagIdDelete;
END $$

DELIMITER $$
 CREATE PROCEDURE SP_GetTagList(
	IN importReferenceIn nvarchar(32)
 )
 BEGIN
	SELECT ti.TagId, ti.ImportReference,TagName,OriginalImagePath FROM Tag_info ti
	WHERE importReferenceIn in ('', ti.ImportReference);
 END $$
 
 DELIMITER $$
 CREATE PROCEDURE SP_GetTagDetail(
	IN tagIdIn BIGINT
 )
 BEGIN
	SELECT ti.img FROM Tag_Image ti WHERE ti.TagId=tagidIn;
    SELECT WordId,OCRDescription,Replacement,Suggestions,Vertices,Category FROM Tag_Word w Where w.TagId=tagIdIn;
 END $$

DELIMITER ;
