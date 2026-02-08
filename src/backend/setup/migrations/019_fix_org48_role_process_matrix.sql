-- Migration 019: Fix Organization 48's Role-Process Matrix Values
-- Date: 2026-01-18
-- Purpose: Align role-process values with SE role cluster standards and create sensible custom values
--
-- Roles in Org 48:
--   456 - Project Coordinator -> SE Cluster 3 (Project Manager)
--   457 - Systems Engineering Lead -> SE Cluster 4 (System Engineer)
--   459 - Quality Assurance Manager -> SE Cluster 8 (Quality Engineer/Manager)
--   460 - Marketing Manager -> Custom (based on Customer Rep + Innovation Mgmt)
--   461 - Human Resources Director -> Custom (based on Internal Support with HR focus)
--   462 - Sales Operations Specialist -> Custom (based on Customer Representative)
--   463 - Financial Controller -> Custom (based on Management)
--   464 - Customer Success Manager -> Custom (based on Customer Representative)
--   468 - Hardware Design Engineer -> SE Cluster 5 (Specialist Developer)
--   469 - Data Analytics Manager -> Custom (data/measurement focus)
--
-- Role-Process Values: 0=Not involved, 1=Supporting, 2=Responsible

BEGIN;

-- =============================================================================
-- ROLE 456: Project Coordinator -> Standard Project Manager (SE Cluster 3)
-- =============================================================================
-- Standard: Responsible for Project Planning/Control, Decision/Risk/Config/Info Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 1;  -- Acquisition
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 2;  -- Supply
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 3;  -- Life Cycle Model Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 4;  -- Infrastructure Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 5;  -- Portfolio Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 6;  -- HR Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 7;  -- Quality Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 8;  -- Knowledge Mgmt
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 9;  -- Project Planning (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 10; -- Project Assessment (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 11; -- Decision Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 12; -- Risk Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 13; -- Config Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 14; -- Info Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 15; -- Measurement
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 16; -- Quality Assurance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 17; -- Business Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 18; -- Stakeholder Needs
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 19; -- System Req Definition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 20; -- System Architecture
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 21; -- Design Definition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 22; -- System Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 23; -- Implementation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 24; -- Integration
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 25; -- Verification
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 26; -- Transition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 27; -- Validation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 28; -- Operation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 29; -- Maintenance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 456 AND iso_process_id = 30; -- Disposal

-- =============================================================================
-- ROLE 457: Systems Engineering Lead -> Standard System Engineer (SE Cluster 4)
-- =============================================================================
-- Standard: Responsible for Decision/Risk/Config Mgmt, System Req/Arch/Design Definition
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 1;  -- Acquisition (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 2;  -- Supply (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 3;  -- Life Cycle Model Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 4;  -- Infrastructure Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 5;  -- Portfolio Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 6;  -- HR Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 7;  -- Quality Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 8;  -- Knowledge Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 9;  -- Project Planning
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 10; -- Project Assessment
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 11; -- Decision Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 12; -- Risk Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 13; -- Config Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 14; -- Info Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 15; -- Measurement
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 16; -- Quality Assurance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 17; -- Business Analysis
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 18; -- Stakeholder Needs (Supporting)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 19; -- System Req (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 20; -- System Arch (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 21; -- Design Definition (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 22; -- System Analysis (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 23; -- Implementation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 24; -- Integration
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 25; -- Verification (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 26; -- Transition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 27; -- Validation
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 28; -- Operation (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 29; -- Maintenance (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 457 AND iso_process_id = 30; -- Disposal

-- =============================================================================
-- ROLE 459: Quality Assurance Manager -> Standard Quality Engineer/Manager (SE Cluster 8)
-- =============================================================================
-- Standard: Responsible for Quality Mgmt and Quality Assurance, Supporting Verification/Validation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 1;  -- Acquisition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 2;  -- Supply
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 3;  -- Life Cycle Model Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 4;  -- Infrastructure Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 5;  -- Portfolio Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 6;  -- HR Mgmt
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 7;  -- Quality Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 8;  -- Knowledge Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 9;  -- Project Planning
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 10; -- Project Assessment
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 11; -- Decision Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 12; -- Risk Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 13; -- Config Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 14; -- Info Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 15; -- Measurement
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 16; -- Quality Assurance (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 17; -- Business Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 18; -- Stakeholder Needs
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 19; -- System Req
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 20; -- System Arch
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 21; -- Design Definition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 22; -- System Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 23; -- Implementation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 24; -- Integration
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 25; -- Verification (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 26; -- Transition
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 27; -- Validation (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 28; -- Operation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 29; -- Maintenance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 459 AND iso_process_id = 30; -- Disposal

-- =============================================================================
-- ROLE 468: Hardware Design Engineer -> Standard Specialist Developer (SE Cluster 5)
-- =============================================================================
-- Standard: Responsible for Design Definition and Implementation, Supporting other tech processes
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 1;  -- Acquisition (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 2;  -- Supply
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 3;  -- Life Cycle Model Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 4;  -- Infrastructure Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 5;  -- Portfolio Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 6;  -- HR Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 7;  -- Quality Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 8;  -- Knowledge Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 9;  -- Project Planning
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 10; -- Project Assessment
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 11; -- Decision Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 12; -- Risk Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 13; -- Config Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 14; -- Info Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 15; -- Measurement (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 16; -- Quality Assurance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 17; -- Business Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 18; -- Stakeholder Needs
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 19; -- System Req (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 20; -- System Arch (Supporting)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 21; -- Design Definition (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 22; -- System Analysis
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 23; -- Implementation (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 24; -- Integration
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 25; -- Verification (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 26; -- Transition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 27; -- Validation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 28; -- Operation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 29; -- Maintenance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 468 AND iso_process_id = 30; -- Disposal

-- =============================================================================
-- ROLE 460: Marketing Manager -> Custom (Customer-facing, market/stakeholder focus)
-- =============================================================================
-- Focus: Supply, Stakeholder Needs, Transition (go-to-market), Business Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 1;  -- Acquisition
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 2;  -- Supply (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 3;  -- Life Cycle Model Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 4;  -- Infrastructure Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 5;  -- Portfolio Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 6;  -- HR Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 7;  -- Quality Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 8;  -- Knowledge Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 9;  -- Project Planning
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 10; -- Project Assessment
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 11; -- Decision Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 12; -- Risk Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 13; -- Config Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 14; -- Info Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 15; -- Measurement
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 16; -- Quality Assurance
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 17; -- Business Analysis (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 18; -- Stakeholder Needs (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 19; -- System Req
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 20; -- System Arch
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 21; -- Design Definition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 22; -- System Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 23; -- Implementation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 24; -- Integration
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 25; -- Verification
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 26; -- Transition (RESPONSIBLE - go to market)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 27; -- Validation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 28; -- Operation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 29; -- Maintenance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 460 AND iso_process_id = 30; -- Disposal

-- =============================================================================
-- ROLE 461: Human Resources Director -> Custom (HR-focused, Internal Support)
-- =============================================================================
-- Focus: HR Management (Responsible), Infrastructure (Supporting), Knowledge Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 1;  -- Acquisition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 2;  -- Supply
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 3;  -- Life Cycle Model Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 4;  -- Infrastructure Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 5;  -- Portfolio Mgmt
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 6;  -- HR Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 7;  -- Quality Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 8;  -- Knowledge Mgmt (Supporting - training)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 9;  -- Project Planning
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 10; -- Project Assessment
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 11; -- Decision Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 12; -- Risk Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 13; -- Config Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 14; -- Info Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 15; -- Measurement
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 16; -- Quality Assurance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 17; -- Business Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 18; -- Stakeholder Needs
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 19; -- System Req
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 20; -- System Arch
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 21; -- Design Definition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 22; -- System Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 23; -- Implementation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 24; -- Integration
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 25; -- Verification
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 26; -- Transition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 27; -- Validation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 28; -- Operation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 29; -- Maintenance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 461 AND iso_process_id = 30; -- Disposal

-- =============================================================================
-- ROLE 462: Sales Operations Specialist -> Custom (Customer-facing, similar to Customer Rep)
-- =============================================================================
-- Focus: Supply, Stakeholder Needs, Transition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 1;  -- Acquisition
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 2;  -- Supply (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 3;  -- Life Cycle Model Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 4;  -- Infrastructure Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 5;  -- Portfolio Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 6;  -- HR Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 7;  -- Quality Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 8;  -- Knowledge Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 9;  -- Project Planning
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 10; -- Project Assessment
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 11; -- Decision Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 12; -- Risk Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 13; -- Config Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 14; -- Info Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 15; -- Measurement
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 16; -- Quality Assurance
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 17; -- Business Analysis (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 18; -- Stakeholder Needs (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 19; -- System Req
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 20; -- System Arch
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 21; -- Design Definition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 22; -- System Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 23; -- Implementation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 24; -- Integration
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 25; -- Verification
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 26; -- Transition (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 27; -- Validation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 28; -- Operation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 29; -- Maintenance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 462 AND iso_process_id = 30; -- Disposal

-- =============================================================================
-- ROLE 463: Financial Controller -> Custom (Management-like, financial focus)
-- =============================================================================
-- Focus: Portfolio Mgmt (budgets), Decision Mgmt, Project Assessment (financial oversight)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 1;  -- Acquisition
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 2;  -- Supply (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 3;  -- Life Cycle Model Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 4;  -- Infrastructure Mgmt
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 5;  -- Portfolio Mgmt (RESPONSIBLE - budgets)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 6;  -- HR Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 7;  -- Quality Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 8;  -- Knowledge Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 9;  -- Project Planning
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 10; -- Project Assessment (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 11; -- Decision Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 12; -- Risk Mgmt (Supporting - financial risk)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 13; -- Config Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 14; -- Info Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 15; -- Measurement (Supporting - metrics)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 16; -- Quality Assurance
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 17; -- Business Analysis (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 18; -- Stakeholder Needs
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 19; -- System Req
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 20; -- System Arch
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 21; -- Design Definition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 22; -- System Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 23; -- Implementation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 24; -- Integration
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 25; -- Verification
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 26; -- Transition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 27; -- Validation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 28; -- Operation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 29; -- Maintenance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 463 AND iso_process_id = 30; -- Disposal

-- =============================================================================
-- ROLE 464: Customer Success Manager -> Custom (Customer-focused, similar to Customer Rep)
-- =============================================================================
-- Focus: Supply, Stakeholder Needs, Transition, Operation (customer success post-launch)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 1;  -- Acquisition
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 2;  -- Supply (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 3;  -- Life Cycle Model Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 4;  -- Infrastructure Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 5;  -- Portfolio Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 6;  -- HR Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 7;  -- Quality Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 8;  -- Knowledge Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 9;  -- Project Planning
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 10; -- Project Assessment
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 11; -- Decision Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 12; -- Risk Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 13; -- Config Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 14; -- Info Mgmt (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 15; -- Measurement
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 16; -- Quality Assurance (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 17; -- Business Analysis (Supporting)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 18; -- Stakeholder Needs (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 19; -- System Req
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 20; -- System Arch
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 21; -- Design Definition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 22; -- System Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 23; -- Implementation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 24; -- Integration
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 25; -- Verification
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 26; -- Transition (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 27; -- Validation (Supporting)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 28; -- Operation (Supporting - customer success)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 29; -- Maintenance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 464 AND iso_process_id = 30; -- Disposal

-- =============================================================================
-- ROLE 469: Data Analytics Manager -> Custom (Data/Measurement focus)
-- =============================================================================
-- Focus: Measurement, Info Mgmt, Knowledge Mgmt, System Analysis
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 1;  -- Acquisition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 2;  -- Supply
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 3;  -- Life Cycle Model Mgmt
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 4;  -- Infrastructure Mgmt (Supporting - data infra)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 5;  -- Portfolio Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 6;  -- HR Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 7;  -- Quality Mgmt
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 8;  -- Knowledge Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 9;  -- Project Planning
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 10; -- Project Assessment (Supporting - metrics)
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 11; -- Decision Mgmt (Supporting - data-driven)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 12; -- Risk Mgmt
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 13; -- Config Mgmt
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 14; -- Info Mgmt (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 2 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 15; -- Measurement (RESPONSIBLE)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 16; -- Quality Assurance
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 17; -- Business Analysis (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 18; -- Stakeholder Needs
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 19; -- System Req
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 20; -- System Arch
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 21; -- Design Definition
UPDATE role_process_matrix SET role_process_value = 1 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 22; -- System Analysis (Supporting)
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 23; -- Implementation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 24; -- Integration
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 25; -- Verification
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 26; -- Transition
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 27; -- Validation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 28; -- Operation
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 29; -- Maintenance
UPDATE role_process_matrix SET role_process_value = 0 WHERE organization_id = 48 AND role_cluster_id = 469 AND iso_process_id = 30; -- Disposal

COMMIT;

-- Verification
DO $$
DECLARE
    role_count INTEGER;
    updated_entries INTEGER;
BEGIN
    SELECT COUNT(DISTINCT role_cluster_id) INTO role_count
    FROM role_process_matrix WHERE organization_id = 48;

    SELECT COUNT(*) INTO updated_entries
    FROM role_process_matrix WHERE organization_id = 48;

    RAISE NOTICE '================================================================';
    RAISE NOTICE '[SUCCESS] Migration 019 completed';
    RAISE NOTICE '================================================================';
    RAISE NOTICE 'Organization 48 role-process matrix updated:';
    RAISE NOTICE '  - Roles updated: %', role_count;
    RAISE NOTICE '  - Total entries: %', updated_entries;
    RAISE NOTICE '';
    RAISE NOTICE 'Roles with SE Cluster mapping (standard values applied):';
    RAISE NOTICE '  - 456 Project Coordinator -> Project Manager';
    RAISE NOTICE '  - 457 Systems Engineering Lead -> System Engineer';
    RAISE NOTICE '  - 459 Quality Assurance Manager -> Quality Engineer/Manager';
    RAISE NOTICE '  - 468 Hardware Design Engineer -> Specialist Developer';
    RAISE NOTICE '';
    RAISE NOTICE 'Custom roles (sensible values created):';
    RAISE NOTICE '  - 460 Marketing Manager';
    RAISE NOTICE '  - 461 Human Resources Director';
    RAISE NOTICE '  - 462 Sales Operations Specialist';
    RAISE NOTICE '  - 463 Financial Controller';
    RAISE NOTICE '  - 464 Customer Success Manager';
    RAISE NOTICE '  - 469 Data Analytics Manager';
    RAISE NOTICE '================================================================';
END $$;
