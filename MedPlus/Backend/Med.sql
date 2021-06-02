CREATE TABLE `Stafes` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `job_code` char(1),
  `name` nvarchar(10),
  `passwd` char(32)
);

CREATE TABLE `Patients` (
  `personal_id` char(10) PRIMARY KEY,
  `name` nvarchar(10)
);

CREATE TABLE `MedList` (
  `code` char(6) PRIMARY KEY,
  `img` varchar(255),
  `ch_name` nvarchar(30),
  `product_name` nvarchar(30),
  `type` nvarchar(10),
  `color` nvarchar(10),
  `shape` nvarchar(10),
  `notch` char(1),
  `print` nvarchar(10)
);

CREATE TABLE `MKUPPrescription` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `PID` int,
  `med_code` char(6)
);

CREATE TABLE `Prescription` (
  `PID` int PRIMARY KEY AUTO_INCREMENT,
  `patients_id` char(10),
  `stafes_id` int,
  `type` nchar(2),
  `timestamp` timestamp
);

CREATE TABLE `Detection` (
  `DID` int PRIMARY KEY AUTO_INCREMENT,
  `PID` int,
  `stafes_id` int,
  `machine` char(32),
  `timestamp` timestamp
);

CREATE TABLE `result` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `DID` int,
  `med_code` char(6)
);

# ALTER TABLE `MKUPPrescription` ADD FOREIGN KEY (`med_code`) REFERENCES `MedList` (`code`);
#
# ALTER TABLE `MKUPPrescription` ADD FOREIGN KEY (`PID`) REFERENCES `Prescription` (`PID`);
#
# ALTER TABLE `Prescription` ADD FOREIGN KEY (`stafes_id`) REFERENCES `Stafes` (`id`);
#
# ALTER TABLE `Prescription` ADD FOREIGN KEY (`patients_id`) REFERENCES `Patients` (`personal_id`);
#
# ALTER TABLE `Detection` ADD FOREIGN KEY (`PID`) REFERENCES `Prescription` (`PID`);
#
# ALTER TABLE `Detection` ADD FOREIGN KEY (`stafes_id`) REFERENCES `Stafes` (`id`);
#
# ALTER TABLE `result` ADD FOREIGN KEY (`DID`) REFERENCES `Detection` (`DID`);
#
# ALTER TABLE `result` ADD FOREIGN KEY (`med_code`) REFERENCES `MedList` (`code`);
