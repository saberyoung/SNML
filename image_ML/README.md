README

1. Machine learning algorithm for image classfication, Abstract.
1.1 Pre-ML process(memory): Recording images and their classification as the memory database.
1.2 ML judging process: Divide the memory database to 2 parts:trainning set and testing set. One can use the trainning set to do ML memory and test with the testing set to know the performance of the ML.
1.3 ML predict process: One can use the memory from step 1 to do ML memory and test with the unknown images.

2. Machine learning algorithm for image classfication, Usage.
2.1 All the codes in the bin&bin2 can be used separately.
2.2 Set the parameters in ini.default and use ml.py.

  Recommand: modify ini.default and then run ml.py. Some parameters describe as following:
  [global]
	run: 1. use all non 1 images(classifified already, check dlt40.classification table) after one JD from dlt40.candidates table as the memory.
             2. use all 1 images(not classifified) after one JD do classification now and let them to be the memory.
	     #For both run1 and run2, we should do memory first and then use the ML memory to do lots of things.
		the difference above is the different way to do memory. Then for both run1 and run2, one can do judge or predict, the JD parameter from [global] is used to define the images for the predit part. The JD and JDdiff from [run2] is used to select images for the memory.
	area_factor: one need a feature and flag to define a candidate, for image ML case, the feature would be the pixel value array around the center of candidate, the flag shoule be the type of source. The area_factor defines the pixel value array, eg. area_factor=20 means the 20*20 array around the center pixel for one candidate was stored as the feature.
	JD: would be used to request from the database. Do mysql from candidates table like 'where jd>'+str(JD).
	ML_model: Machine learning model selection, only 4 models considered till now.
  [ML]
	stored all the parameters would be used by the machine learning algorithm.
  [run2]
	parameters for run=2
	classification
	JD                 
	JDdiff
	area_factor

3. Machine learning algorithm for image classfication, structure.
   use ml.py and change parameters in ini.default. They just call the python codes from bin and bin2.
   memory directory help to store the memory. For run1, I store the memory file like memory/Xy_raw_2457754_20.npz, means the memory is for all the images after JD=2457754 and the area_factor=20. Once memory done, this part would be skipped next time but you can also redo it by using clobber parameters.
   For run2, I use the mysql directly to store the memory. After one finish memory, they are stored in the dlt40.ML_candidates table, within targetsid, classificationid and imglist where imglist is an array with all the dlt40.candidate ID for this field.
