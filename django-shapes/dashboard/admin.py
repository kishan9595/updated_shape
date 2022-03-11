from django.contrib import admin
from .models import *
# Register your models here.
class ClientTableAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'gender','dob', 'age', 'email', 'phone', 'alternate_phone', 'mother_tongue', 'father_name', 'mother_name', 'address', 'branch', 'created_on', 'created_by', 'modified_on', 'modified_by', 'discontinious', 'discontinious_on','assessment', 'slot_time_from','slot_time_to','theropy','chief_complaints','diagnosis','remarks']


admin.site.register(ClientTable, ClientTableAdmin)



class AssessmentTableAdmin(admin.ModelAdmin):
    list_display = ['id','clienttable', 'therapist', 'date_of_assessment','prenatal_history', 'family_history', 'development_history', 'school_history', 'tests_administered', 'test_results', 'behavioural_observation', 'impression', 'recommendations', 'created_on', 'created_by', 'modified_on', 'modified_by', 'email_sent', 'version', 'Status']


admin.site.register(Assesment, AssessmentTableAdmin)


class STAssesmentAdmin(admin.ModelAdmin):
    list_display = ['id','clienttable', 'therapist', 'babbling','first_word', 'main_mode_comm', 'family_history', 'motor_developments', 'oro_peripheral_mechanism', 'vegetative_skills', 'vision', 'hearing', 'response_to_name_call', 'environmental_sounds', 'eye_contact', 'attention_to_sound', 'imitation_to_body_movements', 'imitation_to_speech', 'attention_level', 'social_smile', 'initiates_interaction', 'receptive_language','expressive_language', 'provisional_diagnosis', 'recommendations', 'reels_RL_score', 'reels_EL_score', 'tests_administered', 'Status']


admin.site.register(STAssesment, STAssesmentAdmin)

class OTAssesmentAdmin(admin.ModelAdmin):
    list_display = ['id','clienttable', 'therapist', 'date_of_assessment','presenting_complaints', 'milestone_development', 'behavior_cognition', 'cognitive_skills', 'kinaesthesia', 'Status']


admin.site.register(OTAssesment, OTAssesmentAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ['id','username', 'department', 'password', 'created_by']


admin.site.register(User, UserAdmin)