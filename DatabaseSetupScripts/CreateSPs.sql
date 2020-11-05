
DROP PROCEDURE IF EXISTS SP_AddTag;
DROP PROCEDURE IF EXISTS SP_UpdateWord;
DROP PROCEDURE IF EXISTS SP_DeleteTag;
DROP PROCEDURE IF EXISTS SP_GetTagList;
DROP PROCEDURE IF EXISTS SP_GetTagDetail;

DELIMITER $$

 CREATE PROCEDURE SP_AddTag(
	IN originalImagePathIn VARCHAR(255),
    IN processingTimeIn DECIMAL(9,3),
    IN imgIn LONGBLOB,
    IN wordsInfoAsXMLIn LONGTEXT
 )
 BEGIN
	INSERT INTO Tag_Info(OriginalImagePath,ProcessingTime,Img)
	VALUES (originalImagePathIn,processingTimeIn,UNHEX(imgIn));
	SELECT LAST_INSERT_ID() INTO @newTagId;
    
	SET @COUNT = (SELECT EXTRACTVALUE(wordsInfoAsXMLIn,'COUNT(//words/word)'));
    SET @I = 1;
    WHILE(@I <= @COUNT) DO

        INSERT INTO Tag_Word(TagId,WordIndex,OCRDescription,Replacement,Suggestions,Vertices,Category)
        SELECT  @newTagId,
				ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/wordIndex')),
				ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/description')),
                ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/replacement')),
                ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/suggestions')),
                ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/vertices')),
                ExtractValue(wordsInfoAsXMLIn,CONCAT('/words/word[',@I,']/category'));
        SET @I = @I + 1;
    END WHILE;
    SELECT @newTagId;
 END $$ 
 
 DELIMITER $$
 CREATE PROCEDURE SP_UpdateWord(
	IN tagidIn BIGINT,
	IN wordIndexIn INT,
	IN replacementIn VARCHAR(50) ,
    IN suggestionsIn VARCHAR(1000),
    IN categoryIn VARCHAR(50)
 )
 BEGIN
	UPDATE Tag_Word tw
    SET tw.Replacement=replacementIn,
		tw.Suggestions=suggestionsIn,
		tw.Category=categoryIn,
        tw.LastUpdatedTimeStamp=NOW()
    WHERE tw.WordIndex=wordIndexIn and tw.TagId=tagidIn;
 END $$
 
DELIMITER $$
 CREATE PROCEDURE SP_DeleteTag(
	IN tagIdDelete BIGINT
 )
 BEGIN
	DELETE FROM Tag_Word WHERE TagId=tagIdDelete;
    DELETE FROM Tag_Info WHERE TagId=tagIdDelete;
END $$

DELIMITER $$
 CREATE PROCEDURE SP_GetTagList(
	IN  importDateIn VARCHAR(10) 
 )
 BEGIN
	SELECT ti.TagId, ti.ImportDate,ti.OriginalImagePath FROM Tag_info ti
	WHERE importDateIn in ('', ti.ImportDate);
 END $$
 
 DELIMITER $$
 CREATE PROCEDURE SP_GetTagDetail(
	IN tagIdIn BIGINT
 )
 BEGIN
	SELECT ti.Img, ti.OriginalImagePath,ti.ProcessingTime,ti.ImportDate FROM Tag_Info ti WHERE ti.TagId=tagidIn;
	SELECT WordIndex,OCRDescription,Replacement,Suggestions,Vertices,Category FROM Tag_Word w Where w.TagId=tagIdIn;
 END $$
 
DELIMITER ;
