from pydantic import BaseModel
from typing import List, Optional


class OrgStudyIdInfo(BaseModel):
    id: Optional[str] = None


class SecondaryIdInfo(BaseModel):
    id: Optional[str] = None


class Organization(BaseModel):
    full_name: Optional[str] = None
    class_: Optional[str] = None  # class is a reserved keyword, hence the underscore


class IdentificationModule(BaseModel):
    nct_id: Optional[str] = None
    org_study_id_info: Optional[OrgStudyIdInfo] = None
    secondary_id_infos: List[SecondaryIdInfo] = []
    organization: Optional[Organization] = None
    brief_title: Optional[str] = None
    official_title: Optional[str] = None
    acronym: Optional[str] = None


class ExpandedAccessInfo(BaseModel):
    has_expanded_access: Optional[bool] = None


class DateStruct(BaseModel):
    date: Optional[str] = None
    type: Optional[str] = None


class StatusModule(BaseModel):
    status_verified_date: Optional[str] = None
    overall_status: Optional[str] = None
    expanded_access_info: Optional[ExpandedAccessInfo] = None
    start_date_struct: Optional[DateStruct] = None
    primary_completion_date_struct: Optional[DateStruct] = None
    completion_date_struct: Optional[DateStruct] = None
    study_first_submit_date: Optional[str] = None
    study_first_submit_qc_date: Optional[str] = None
    study_first_post_date_struct: Optional[DateStruct] = None
    last_update_submit_date: Optional[str] = None
    last_update_post_date_struct: Optional[DateStruct] = None


class ResponsibleParty(BaseModel):
    old_name_title: Optional[str] = None
    old_organization: Optional[str] = None


class LeadSponsor(BaseModel):
    name: Optional[str] = None
    class_: Optional[str] = None


class SponsorCollaboratorsModule(BaseModel):
    responsible_party: Optional[ResponsibleParty] = None
    lead_sponsor: Optional[LeadSponsor] = None


class OversightModule(BaseModel):
    oversight_has_dmc: Optional[bool] = None


class DescriptionModule(BaseModel):
    brief_summary: Optional[str] = None


class ConditionsModule(BaseModel):
    conditions: List[str] = []


class MaskingInfo(BaseModel):
    masking: Optional[str] = None
    who_masked: List[str] = []


class DesignInfo(BaseModel):
    allocation: Optional[str] = None
    intervention_model: Optional[str] = None
    primary_purpose: Optional[str] = None
    masking_info: Optional[MaskingInfo] = None


class EnrollmentInfo(BaseModel):
    count: Optional[int] = None
    type: Optional[str] = None


class DesignModule(BaseModel):
    study_type: Optional[str] = None
    phases: List[str] = []
    design_info: Optional[DesignInfo] = None
    enrollment_info: Optional[EnrollmentInfo] = None


class ArmGroup(BaseModel):
    label: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    intervention_names: List[str] = []


class Intervention(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    arm_group_labels: List[str] = []


class ArmsInterventionsModule(BaseModel):
    arm_groups: List[ArmGroup] = []
    interventions: List[Intervention] = []


class Outcome(BaseModel):
    measure: Optional[str] = None
    time_frame: Optional[str] = None


class OutcomesModule(BaseModel):
    primary_outcomes: List[Outcome] = []
    secondary_outcomes: List[Outcome] = []


class EligibilityModule(BaseModel):
    eligibility_criteria: Optional[str] = None
    healthy_volunteers: Optional[bool] = None
    sex: Optional[str] = None
    minimum_age: Optional[str] = None
    maximum_age: Optional[str] = None
    std_ages: List[str] = []


class Official(BaseModel):
    name: Optional[str] = None
    affiliation: Optional[str] = None
    role: Optional[str] = None


class GeoPoint(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None


class Location(BaseModel):
    facility: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None
    geo_point: Optional[GeoPoint] = None


class ContactsLocationsModule(BaseModel):
    overall_officials: List[Official] = []
    locations: List[Location] = []


class Reference(BaseModel):
    pmid: Optional[str] = None
    type: Optional[str] = None
    citation: Optional[str] = None


class ReferencesModule(BaseModel):
    references: List[Reference] = []


class ProtocolSection(BaseModel):
    identification_module: Optional[IdentificationModule] = None
    status_module: Optional[StatusModule] = None
    sponsor_collaborators_module: Optional[SponsorCollaboratorsModule] = None
    oversight_module: Optional[OversightModule] = None
    description_module: Optional[DescriptionModule] = None
    conditions_module: Optional[ConditionsModule] = None
    design_module: Optional[DesignModule] = None
    arms_interventions_module: Optional[ArmsInterventionsModule] = None
    outcomes_module: Optional[OutcomesModule] = None
    eligibility_module: Optional[EligibilityModule] = None
    contacts_locations_module: Optional[ContactsLocationsModule] = None
    references_module: Optional[ReferencesModule] = None


class MiscInfoModule(BaseModel):
    version_holder: Optional[str] = None


class Mesh(BaseModel):
    id: Optional[str] = None
    term: Optional[str] = None


class Ancestor(BaseModel):
    id: Optional[str] = None
    term: Optional[str] = None


class BrowseLeaf(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    relevance: Optional[str] = None
    as_found: Optional[str] = None


class BrowseBranch(BaseModel):
    abbrev: Optional[str] = None
    name: Optional[str] = None


class ConditionBrowseModule(BaseModel):
    meshes: List[Mesh] = []
    ancestors: List[Ancestor] = []
    browse_leaves: List[BrowseLeaf] = []
    browse_branches: List[BrowseBranch] = []


class InterventionBrowseModule(BaseModel):
    meshes: List[Mesh] = []
    ancestors: List[Ancestor] = []
    browse_leaves: List[BrowseLeaf] = []
    browse_branches: List[BrowseBranch] = []


class DerivedSection(BaseModel):
    misc_info_module: Optional[MiscInfoModule] = None
    condition_browse_module: Optional[ConditionBrowseModule] = None
    intervention_browse_module: Optional[InterventionBrowseModule] = None


class ClinicalTrialData(BaseModel):
    protocol_section: Optional[ProtocolSection] = None
    derived_section: Optional[DerivedSection] = None
    has_results: Optional[bool] = None
