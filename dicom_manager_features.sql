

--*****************************************************************************
-- Compute Features
--*****************************************************************************


-- create Features table
CREATE TEMPORARY TABLE IF NOT EXISTS Features AS 
SELECT
	id,
	NumberOfDicoms,
	ImageType,
	StudyDate,
	substr(StudyDate, 1,4) || "-" || substr(StudyDate,5,2)  || "-" || substr(StudyDate, 7,2) AS Study_date,
	AccessionNumber,
	Modality,
	Manufacturer,
	InstitutionName,
	StationName,
	StudyDescription,
	SeriesDescription,
	CASE
		WHEN
			(
				SeriesDescription LIKE '%MPRAGE%' 
				OR
				SeriesDescription LIKE '%MP RAGE%'
			)
			AND
			(
				SeriesDescription NOT LIKE '%TOF%'
				AND
				SeriesDescription NOT LIKE '%FSPGR%'
				AND
				SeriesDescription NOT LIKE '%POST%GAD%'
				AND
				SeriesDescription NOT LIKE '%POST%GD%'
				AND
				SeriesDescription NOT LIKE '%+GAD%'
				AND
				SeriesDescription NOT LIKE '%+GD%'
				AND
				SeriesDescription NOT LIKE '%POST%CC%'
				AND
				SeriesDescription NOT LIKE '%+C%'
				AND
				SeriesDescription NOT LIKE '%+ C%'
				AND
				SeriesDescription NOT LIKE '%C+%'
				AND
				SeriesDescription NOT LIKE '%POST%INJ%'
				AND
				SeriesDescription NOT LIKE '%FOLLOW%INJ%'
				AND
				SeriesDescription NOT LIKE '%+%CC%'
				AND
				SeriesDescription NOT LIKE '%CC'
				AND
				SeriesDescription NOT LIKE '%+%ml%'
			)
		THEN '#MPRAGE'
		WHEN
			(
				SeriesDescription LIKE '%SPGR%' 
			)
			AND
			(
				SeriesDescription NOT LIKE '%TOF%'
				AND
				SeriesDescription NOT LIKE '%FSPGR%'
				AND
				SeriesDescription NOT LIKE '%POST%GAD%'
				AND
				SeriesDescription NOT LIKE '%POST%GD%'
				AND
				SeriesDescription NOT LIKE '%+GAD%'
				AND
				SeriesDescription NOT LIKE '%+GD%'
				AND
				SeriesDescription NOT LIKE '%POST%CC%'
				AND
				SeriesDescription NOT LIKE '%+C%'
				AND
				SeriesDescription NOT LIKE '%+ C%'
				AND
				SeriesDescription NOT LIKE '%C+%'
				AND
				SeriesDescription NOT LIKE '%POST%INJ%'
				AND
				SeriesDescription NOT LIKE '%FOLLOW%INJ%'
				AND
				SeriesDescription NOT LIKE '%+%CC%'
				AND
				SeriesDescription NOT LIKE '%CC'
				AND
				SeriesDescription NOT LIKE '%+%ml%'
			)
		THEN '#SPGR'
		WHEN
			(
				SeriesDescription LIKE '%BRAVO%' 
			)
			AND
			(
				SeriesDescription NOT LIKE '%TOF%'
				AND
				SeriesDescription NOT LIKE '%FSPGR%'
				AND
				SeriesDescription NOT LIKE '%POST%GAD%'
				AND
				SeriesDescription NOT LIKE '%POST%GD%'
				AND
				SeriesDescription NOT LIKE '%+GAD%'
				AND
				SeriesDescription NOT LIKE '%+GD%'
				AND
				SeriesDescription NOT LIKE '%POST%CC%'
				AND
				SeriesDescription NOT LIKE '%+C%'
				AND
				SeriesDescription NOT LIKE '%+ C%'
				AND
				SeriesDescription NOT LIKE '%C+%'
				AND
				SeriesDescription NOT LIKE '%POST%INJ%'
				AND
				SeriesDescription NOT LIKE '%FOLLOW%INJ%'
				AND
				SeriesDescription NOT LIKE '%+%CC%'
				AND
				SeriesDescription NOT LIKE '%CC'
				AND
				SeriesDescription NOT LIKE '%+%ml%'
			)
		THEN '#BRAVO'
		WHEN
			(
				SeriesDescription LIKE '%DTI%'
				OR
				SeriesDescription LIKE '%DWI%'
				OR
				SeriesDescription LIKE '%Diffusion%'
			)
			AND
			(
				SeriesDescription NOT LIKE '%ADC%'
				AND
				SeriesDescription NOT LIKE '%TRACE%'
				AND
				SeriesDescription NOT LIKE '%EXP%'
				AND
				SeriesDescription NOT LIKE '%FA%'
				AND
				SeriesDescription NOT LIKE '%LOWB%'
			)
		THEN '#DWI'
		WHEN
			(
				SeriesDescription LIKE 'FA'
				OR
				SeriesDescription LIKE 'FA %'
				OR
				SeriesDescription LIKE '_FA'
				OR
				(
					SeriesDescription LIKE '%FA%'
					AND
					(
						SeriesDescription LIKE '%DWI%'
						OR
						SeriesDescription LIKE '%DIFFUSION%'
						OR
						SeriesDescription LIKE '%DTI%'
					)
					AND
					(
						SeriesDescription NOT LIKE '%FaReg%'
						AND
						SeriesDescription NOT LIKE '%FacReg%'
						AND
						SeriesDescription NOT LIKE '%FaDTI%'
						AND
						SeriesDescription NOT LIKE '%FacDTI%'
					)
				)			
			)
		THEN '#DWI_FA'
		WHEN
			(
				SeriesDescription LIKE '%ADC%'
			)
		THEN '#DWI_ADC' 
		ELSE SeriesDescription
	END AS Series_description,
	ManufacturerModelName,
	PatientID,
	PatientSex,
	PatientAge,
	julianday(substr(StudyDate, 1,4) || "-" || substr(StudyDate,5,2)  || "-" || substr(StudyDate, 7,2)) 
			- julianday(substr(PatientBirthDate, 1,4) || "-" || substr(PatientBirthDate,5,2)  || "-" || substr(PatientBirthDate, 7,2))
			AS Patient_age_in_days,
	MRAcquisitionType,
	AngioFlag,
	SliceThickness,
	cast(SliceThickness AS REAL) AS Slice_thickness,
	RepetitionTime,
	cast(RepetitionTime AS REAL) Repetition_time,
	EchoTime,
	cast(EchoTime AS REAL) Echo_time,
	ImagingFrequency,
	cast(ImagingFrequency AS REAL) Imaging_frequency,
	MagneticFieldStrength,
	CASE 
		WHEN MagneticFieldStrength IS NULL THEN NULL
		WHEN cast(MagneticFieldStrength AS REAL) BETWEEN 0.9 AND 1.1 THEN 1
		WHEN cast(MagneticFieldStrength AS REAL) BETWEEN 9000 AND 11000 THEN 1
		WHEN cast(MagneticFieldStrength AS REAL) BETWEEN 1.4 AND 1.6 THEN 1.5
		WHEN cast(MagneticFieldStrength AS REAL) BETWEEN 14000 AND 16000 THEN 1.5
		WHEN cast(MagneticFieldStrength AS REAL) BETWEEN 2.9 AND 3.1 THEN 3
		WHEN cast(MagneticFieldStrength AS REAL) BETWEEN 29000 AND 31000 THEN 3
		ELSE cast(MagneticFieldStrength AS REAL) 
	END AS Magnetic_field_strength,
	SpacingBetweenSlices,
	cast(SpacingBetweenSlices AS REAL) Spacing_between_slices,
	ProtocolName,
	StudyInstanceUID
FROM
	Series
;




--*****************************************************************************
-- Statistics
--*****************************************************************************


------------------------------------------------------------------------------------------
-- Echo Time Breakdown - DWI
SELECT
	round(cast(Echo_time AS REAL) / 1) * 1 AS TE,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
WHERE
(
	Series_description LIKE '#DWI'
)
AND
(
	TE BETWEEN 97.4 AND 108
)
GROUP BY
	TE



------------------------------------------------------------------------------------------
-- Study Date breakdown
SELECT
	round(cast(StudyDate AS REAL) / 10000) AS StudyYear,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
GROUP BY
	StudyYear


------------------------------------------------------------------------------------------
-- Study Date breakdown - T1
SELECT
	round(cast(StudyDate AS REAL) / 10000) AS StudyYear,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
WHERE
(
	Series_description LIKE '#MPRAGE'
	OR
	Series_description LIKE '#SPGR'
	OR
	Series_description LIKE '#BRAVO'
)
GROUP BY
	StudyYear


------------------------------------------------------------------------------------------
-- Study Date breakdown - DWI
SELECT
	round(cast(StudyDate AS REAL) / 10000) AS StudyYear,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
WHERE
(
	Series_description LIKE '#DWI'
)
AND
(
	Echo_time BETWEEN 97.4 AND 108
)
GROUP BY
	StudyYear


------------------------------------------------------------------------------------------
-- Breakdown of Patient Age in days
SELECT
	Patient_age_in_days,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM
	Features
GROUP BY
	Patient_age_in_days
ORDER BY
	Patient_age_in_days


------------------------------------------------------------------------------------------
-- Breakdown of Patient Age in weeks
SELECT
	round(cast( (Patient_age_in_days / 7) AS INTEGER)) AS Patient_age_in_weeks,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM
	Features
GROUP BY
	Patient_age_in_weeks
ORDER BY
	Patient_age_in_weeks


------------------------------------------------------------------------------------------
-- Breakdown of Patient Age in weeks - T1
SELECT
	round(cast( (Patient_age_in_days / 7) AS INTEGER)) AS Patient_age_in_weeks,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM
	Features
WHERE
(
	Series_description LIKE '#MPRAGE'
	OR
	Series_description LIKE '#SPGR'
	OR
	Series_description LIKE '#BRAVO'
)
GROUP BY
	Patient_age_in_weeks
ORDER BY
	Patient_age_in_weeks


------------------------------------------------------------------------------------------
-- Breakdown of Patient Age in weeks - DWI
SELECT
	round(cast( (Patient_age_in_days / 7) AS INTEGER)) AS Patient_age_in_weeks,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM
	Features
WHERE
(
	Series_description LIKE '#DWI'
)
AND
(
	Echo_time BETWEEN 97.4 AND 108
)
GROUP BY
	Patient_age_in_weeks
ORDER BY
	Patient_age_in_weeks


------------------------------------------------------------------------------------------
-- Breakdown of Patient Age in months
SELECT
	round(cast( (Patient_age_in_days / 30) AS INTEGER)) AS Patient_age_in_months,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM
	Features
GROUP BY
	Patient_age_in_months
ORDER BY
	Patient_age_in_months


------------------------------------------------------------------------------------------
-- Breakdown of Patient Age in months - T1
SELECT
	round(cast( (Patient_age_in_days / 30) AS INTEGER)) AS Patient_age_in_months,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM
	Features
WHERE
(
	Series_description LIKE '#MPRAGE'
	OR
	Series_description LIKE '#SPGR'
	OR
	Series_description LIKE '#BRAVO'
)
GROUP BY
	Patient_age_in_months
ORDER BY
	Patient_age_in_months


------------------------------------------------------------------------------------------
-- Breakdown of Patient Age in months - DWI
SELECT
	round(cast( (Patient_age_in_days / 30) AS INTEGER)) AS Patient_age_in_months,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM
	Features
WHERE
(
	Series_description LIKE '#DWI'
)
AND
(
	Echo_time BETWEEN 97.4 AND 108
)
GROUP BY
	Patient_age_in_months
ORDER BY
	Patient_age_in_months


------------------------------------------------------------------------------------------
-- Breakdown of Patient Age in years
SELECT
	round(cast( (Patient_age_in_days / 365) AS INTEGER)) AS Patient_age_in_years,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM
	Features
GROUP BY
	Patient_age_in_years
ORDER BY
	Patient_age_in_years


------------------------------------------------------------------------------------------
-- Breakdown of Patient Age in years - T1
SELECT
	round(cast( (Patient_age_in_days / 365) AS INTEGER)) AS Patient_age_in_years,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM
	Features
WHERE
(
	Series_description LIKE '#MPRAGE'
	OR
	Series_description LIKE '#SPGR'
	OR
	Series_description LIKE '#BRAVO'
)
GROUP BY
	Patient_age_in_years
ORDER BY
	Patient_age_in_years


------------------------------------------------------------------------------------------
-- Breakdown of Patient Age in years - DWI
SELECT
	round(cast( (Patient_age_in_days / 365) AS INTEGER)) AS Patient_age_in_years,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM
	Features
WHERE
(
	Series_description LIKE '#DWI'
)
AND
(
	Echo_time BETWEEN 97.4 AND 108
)
GROUP BY
	Patient_age_in_years
ORDER BY
	Patient_age_in_years


------------------------------------------------------------------------------------------
-- Institution Name breakdown
SELECT 
	InstitutionName,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
GROUP BY
	InstitutionName


------------------------------------------------------------------------------------------
-- Institution Name breakdown - T1
SELECT 
	InstitutionName,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
WHERE
(
	Series_description LIKE '#MPRAGE'
	OR
	Series_description LIKE '#SPGR'
	OR
	Series_description LIKE '#BRAVO'
)
GROUP BY
	InstitutionName


------------------------------------------------------------------------------------------
-- Manufacturer breakdown
SELECT 
	Manufacturer,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
GROUP BY
	Manufacturer



------------------------------------------------------------------------------------------
-- Manufacturer breakdown - T1
SELECT 
	Manufacturer,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
WHERE
(
	Series_description LIKE '#MPRAGE'
	OR
	Series_description LIKE '#SPGR'
	OR
	Series_description LIKE '#BRAVO'
)
GROUP BY
	Manufacturer



------------------------------------------------------------------------------------------
-- Manufacturer and Model breakdown
SELECT 
	Manufacturer || ' : ' || ManufacturerModelName AS ManufacturerAndModel,
	count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
GROUP BY
	ManufacturerAndModel
ORDER BY
	ManufacturerAndModel


------------------------------------------------------------------------------------------
-- Magnetic Field Strength breakdown
SELECT 
	round(CASE WHEN cast(Magnetic_field_strength AS REAL) > 1000 THEN cast(Magnetic_field_strength AS REAL) / 10000 ELSE cast(Magnetic_field_strength AS REAL) END, 1) AS Magnetic_field_strength,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
GROUP BY
	Magnetic_field_strength
ORDER BY
	Magnetic_field_strength


------------------------------------------------------------------------------------------
-- Magnetic Field Strength breakdown - T1
SELECT 
	round(CASE WHEN cast(Magnetic_field_strength AS REAL) > 1000 THEN cast(Magnetic_field_strength AS REAL) / 10000 ELSE cast(Magnetic_field_strength AS REAL) END, 1) AS Magnetic_field_strength,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
WHERE
(
	Series_description LIKE '#MPRAGE'
	OR
	Series_description LIKE '#SPGR'
	OR
	Series_description LIKE '#BRAVO'
)
GROUP BY
	Magnetic_field_strength
ORDER BY
	Magnetic_field_strength


------------------------------------------------------------------------------------------
-- Slice Thickness breakdown
SELECT 
	round(round(cast(SliceThickness AS REAL) / 0.01) * 0.01, 2) AS SliceThickness,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Series
GROUP BY
	SliceThickness
ORDER BY
	SliceThickness


------------------------------------------------------------------------------------------
-- Slice Thickness breakdown - T1
SELECT 
	round(round(cast(Slice_thickness AS REAL) / 0.01) * 0.01, 2) AS Slice_thickness,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
WHERE
(
	Series_description LIKE '#MPRAGE'
	OR
	Series_description LIKE '#SPGR'
	OR
	Series_description LIKE '#BRAVO'
)
GROUP BY
	Slice_thickness
ORDER BY
	Slice_thickness


------------------------------------------------------------------------------------------
-- Inter-Slice Spacing breakdown
SELECT 
	round(round(cast(Spacing_between_slices AS REAL) / 0.1) * 0.1, 1) AS Spacing_between_slices,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
GROUP BY
	Spacing_between_slices
ORDER BY
	Spacing_between_slices



------------------------------------------------------------------------------------------
-- Inter-Slice Spacing breakdown - T1
SELECT 
	round(round(cast(Spacing_between_slices AS REAL) / 0.1) * 0.1, 1) AS Spacing_between_slices,
	--count(*) AS SeriesN,
	count(DISTINCT StudyInstanceUID) AS StudyN,
	count(DISTINCT PatientID) AS PatientN
FROM 
	Features
WHERE
(
	Series_description LIKE '#MPRAGE'
	OR
	Series_description LIKE '#SPGR'
	OR
	Series_description LIKE '#BRAVO'
)
GROUP BY
	Spacing_between_slices
ORDER BY
	Spacing_between_slices






--*****************************************************************************
-- Searches for potentially useful series
--*****************************************************************************


------------------------------------------------------------------------------------------
-- Potential T1 Series
CREATE TEMPORARY TABLE PotentialSeriesT1 AS
SELECT 
	id
FROM 
	Features								--n=69307
WHERE
	Modality LIKE 'MR'						--n=68918
AND
	Study_date > '2005'						--n=65913
AND
	Patient_age_in_days < 2190--(6 years)	--n=52837
AND
(
	Series_description LIKE '#MPRAGE'
	OR
	Series_description LIKE '#SPGR'
	OR
	Series_description LIKE '#BRAVO'
)											--n=4556
AND
	Magnetic_field_strength = 3				--n=2841
AND
	MRAcquisitionType LIKE '3D'				--n=2822
AND
	Slice_thickness <= 1					--n=2797
AND
	Spacing_between_slices IS NULL			--n=2793
AND
	AngioFlag LIKE 'N'						--n=2793
AND
	NumberOfDicoms > 50						--n=2666
AND
	InstitutionName NOT LIKE 'LI'			--n=2569
;



------------------------------------------------------------------------------------------
-- Visual review of T1 series
CREATE TEMPORARY TABLE QualitySeriesT1 AS
SELECT 
	id
FROM 
	Series
WHERE
	id IN PotentialSeriesT1															--n=2569
AND
	id IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#reviewed%')			--n=
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#artifacts')		--n=
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#badFOV')			--n=
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#lesserOfStudy')	--n=
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#blackImage')		--n=
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#abnormality')		--n=
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#wrongType')		--n=
;



------------------------------------------------------------------------------------------
-- Potential pre-computed ADC series
CREATE TEMPORARY TABLE PotentialSeriesADC AS
SELECT 
	id
FROM 
	Features								--n=69307
WHERE
	Modality LIKE 'MR'						--n=68918
AND
	Study_date > '2005'						--n=65913
AND
	Patient_age_in_days < 2190--(6 years)	--n=52837
AND
	Series_description LIKE '#DWI_ADC'		--n=1991
AND
	Magnetic_field_strength = 3				--n=609
AND
	Slice_thickness <= 2.5					--n=555
AND
	NumberOfDicoms > 50						--n=551
AND
(
	SeriesDescription NOT LIKE '%B=2000%'
	AND
	SeriesDescription NOT LIKE '%B=3000%'
)											--n=549
AND
	InstitutionName NOT LIKE 'LI'			--n=519
;



------------------------------------------------------------------------------------------
-- Visual review of pre-computed ADC series
CREATE TEMPORARY TABLE QualitySeriesADC AS
SELECT 
	id
FROM 
	Series
WHERE
	id IN PotentialSeriesADC														--n=519
AND
	id IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#reviewed%')			--n=519
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#artifacts')		--n=465
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#badFOV')			--n=437
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#lesserOfStudy')	--n=385
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#blackImage')		--n=359
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#abnormality')		--n=271
AND
	id NOT IN (SELECT SeriesId FROM SeriesNotes WHERE Note LIKE '#wrongType')		--n=269
;




