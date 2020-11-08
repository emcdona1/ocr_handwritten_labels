
DROP PROCEDURE IF EXISTS SP_AddTag;
DROP PROCEDURE IF EXISTS SP_UpdateWord;
DROP PROCEDURE IF EXISTS SP_DeleteTag;
DROP PROCEDURE IF EXISTS SP_GetTagList;
DROP PROCEDURE IF EXISTS SP_GetTagDetail;
DROP PROCEDURE IF EXISTS SP_AddBarCodeInfo;
DROP PROCEDURE IF EXISTS SP_GetBarCodeInfo;

DELIMITER $$

 CREATE PROCEDURE SP_AddTag(
	IN originalImagePathIn VARCHAR(255),
    IN processingTimeIn DECIMAL(9,3),
    IN imgIn LONGBLOB,
    IN wordsInfoAsXMLIn LONGTEXT,
    IN barCodeIn VARCHAR(20)
 )
 BEGIN
	SET @ImportDate=(SELECT DATE_FORMAT(NOW(),'%Y-%m-%d'));
	INSERT INTO Tag_Info(BarCode,ImportDate,OriginalImagePath,ProcessingTime,Img)
	VALUES (barCodeIn,@ImportDate,originalImagePathIn,processingTimeIn,UNHEX(imgIn));
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
    IF EXISTS (SELECT 1 FROM  Barcode_Info where Barcode=barCodeIn)
    THEN SELECT @newTagId,@ImportDate,1;
    ELSE SELECT @newTagId,@ImportDate,0;
    END IF;
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
	SELECT ti.Img, ti.OriginalImagePath,ti.ProcessingTime,ti.ImportDate,ti.BarCode,
    bi.IRN,bi.Taxonomy,bi.Collector,bi.Details
    FROM Tag_Info ti 
    LEFT JOIN Barcode_Info bi on ti.BarCode=bi.BarCode
    WHERE ti.TagId=tagidIn;
	SELECT WordIndex,OCRDescription,Replacement,Suggestions,Vertices,Category FROM Tag_Word w Where w.TagId=tagIdIn;
	

 END $$
 
 
 DELIMITER $$
 CREATE PROCEDURE SP_AddBarCodeInfo(
	IN barCodeIn VARCHAR(10),
    IN irnIn BIGINT,
    IN taxonomyIn VARCHAR(100),
    IN collectorIn VARCHAR(100),
    IN detailsIn VARCHAR(1000)
 )
 BEGIN
	INSERT INTO Barcode_Info(BarCode,IRN,Taxonomy,Collector,Details)
	VALUES (barCodeIn,irnIn,taxonomyIn,collectorIn,detailsIn);
END $$

DELIMITER $$
 CREATE PROCEDURE SP_GetBarCodeInfo(
	IN barCodeIn VARCHAR(10)
 )
 BEGIN
	SELECT BarCode,IRN,Taxonomy,Collector,Details
	FROM Barcode_Info bi
	WHERE bi.BarCode=barCodeIn;
END $$

DELIMITER ;
