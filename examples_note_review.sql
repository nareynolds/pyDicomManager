------------------------------------------------------------------------------------------
--useful tags to add to the Notes table
#reviewed:date
#artifacts
#badFOV
#blackImage
#annotations
#abnormality
#lesserOfStudy
#quality:3
#quality:2
#quality:1
#quality:0


------------------------------------------------------------------------------------------
-- initial search for Structural T1 scans for week 0 patients
CREATE TEMPORARY TABLE All_week0_T1_series AS
SELECT DISTINCT
	id--, 									--n=69307
	--InstitutionName,
	--PatientID,
	--AccessionNumber,
	--PatientAge,
	--SeriesDescription
FROM
	Series
WHERE
(
	(
		PatientAge < '007D'
		AND
		PatientAge LIKE '%D%'
	)
	OR
	(
		PatientAge < '002W'
		AND
		PatientAge LIKE '%W%'
	)
)										--n=4029
AND
(
	SeriesDescription LIKE '%MPRAGE%'
	OR 
	SeriesDescription LIKE '%MP RAGE%'
	OR 
	SeriesDescription LIKE '%SPGR%'
	OR 
	SeriesDescription LIKE '%BRAVO%'
)
AND
(
	SeriesDescription NOT LIKE '%TOF%'
	AND
	SeriesDescription NOT LIKE '%POST GD%'
)										--n=293
AND
(
	NumberOfDicoms > 50
)										--n=281
AND
(
	id NOT IN ( SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '%#reviewed%' ) -- look for unreviewed series
)


------------------------------------------------------------------------------------------
-- find reviewed Structural T1 scans for week 0 patients
SELECT DISTINCT
	id--,
	--InstitutionName,
	--PatientID,
	--AccessionNumber,
	--PatientAge,
	--SeriesDescription
FROM
	Series
WHERE
(
	id IN All_week0_T1_series 																--n=205
)
AND
(
		id IN        ( SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '%#reviewed%' )		--n=203
	AND
		id NOT IN ( SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '%#artifacts%' )		--n=109
	AND
		id NOT IN ( SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '%#badFOV%' )			--n=95
	AND
		id NOT IN ( SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '%#annotations%' )		--n=89
	AND
		id NOT IN ( SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '%#abnormality%' )		--n=80
	AND
		id NOT IN ( SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '%#lesserOfStudy%' )	--n=43
	AND
		id NOT IN ( SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '%#blackImage%' )		--n=40
)
	




























