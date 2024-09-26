from rest_framework import serializers

from backend.welfare_intervention.intervention.models import CovidAssistance, vest_db, activity_db, item_db, intervention, sweap_assistance, \
    sweap_gratuity, employee_assistance_sop, health_profile, sweap_gratuity, incidentreport_db, Sweap_membership


class sweap_membership_serialize(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    emp_id = serializers.CharField(source='emp.id_number',read_only=True)
    full_name = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)
    id_number = serializers.CharField(source='emp.id_number', read_only=True)
    picture = serializers.CharField(source='emp.picture', read_only=True)
    gender = serializers.CharField(source='emp.pi.get_gender', read_only=True, allow_null=True)
    employment_status = serializers.CharField(source='emp.empstatus.name', read_only=True, allow_null=True)
    position = serializers.CharField(source='emp.position.name', read_only=True, allow_null=True)
    section = serializers.CharField(source='emp.section.sec_name', read_only=True, allow_null=True)
    encodedby = serializers.CharField(source='encodedby.get_fullname', read_only=True, allow_null=True)
    dateadded = serializers.DateTimeField(format="%b %d, %Y %H:%M:%S %p", read_only=True)

    class Meta:
        model = Sweap_membership
        fields = ['id','emp_id', 'full_name', 'id_number', 'picture', 'gender', 'employment_status', 'position', 'section', 'encodedby', 'dateadded']

class item_db_serialize(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    item = serializers.CharField(read_only=True)
    activity = serializers.CharField(source='activity.activity',read_only=True)
    # user_id = serializers.py.CharField(source='pi.user.id', read_only=True)
    inventory = serializers.IntegerField(read_only=True)
    class Meta:
        model = item_db
        fields = '__all__'

class vest_db_serialize(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    emp_id = serializers.CharField(source='emp.id_number',read_only=True)
    full_name = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)
    division = serializers.CharField(source='emp.section.div.div_name', read_only=True, allow_null=True)
    date_borrowed = serializers.DateField(format="%b %d, %Y", read_only=True)
    date_returned = serializers.DateField(format="%b %d, %Y", read_only=True)
    status = serializers.IntegerField(read_only=True)

    class Meta:
        model = vest_db
        fields = ['id','emp_id', 'full_name', 'division', 'no_of_days', 'status','date_borrowed','date_returned']


class intervention_db_serialize(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    emp_id = serializers.CharField(source='emp.id_number',read_only=True)
    fname = serializers.CharField(source='emp.pi.user.first_name')
    lname = serializers.CharField(source='emp.pi.user.last_name')
    division = serializers.CharField(source='emp.section.div.div_name', read_only=True, allow_null=True)
    sex = serializers.CharField(source='emp.pi.gender')
    intervention = serializers.CharField(source='activity.activity')
    item = serializers.CharField(source='item.item')
    total = serializers.IntegerField(read_only=True)
    stocks = serializers.IntegerField(source='item.inventory')
    full_name = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)

    class Meta:
        model = intervention
        fields = ['id','emp_id','full_name','fname','lname','division','sex','intervention','item','total','stocks']

class covid_assistance_serialize(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    emp_id = serializers.CharField(source='emp.id_number', read_only=True)
    full_name = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)
    caseofemp = serializers.CharField(read_only=True,  allow_null=True)
    sex = serializers.CharField(source='emp.pi.gender')
    division = serializers.CharField(source='emp.section.div.div_name', read_only=True, allow_null=True)
    provision = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True, source='emp.pi.user.email')
    phone = serializers.CharField(read_only=True,source='emp.pi.mobile_no')
    start = serializers.DateField(format="%b %d, %Y", read_only=True)
    end = serializers.DateField(format="%b %d, %Y", read_only=True)

    class Meta:
        model = CovidAssistance
        fields = ['id','emp_id','full_name','caseofemp','sex','division','provision','email','phone','start','end']


class sweap_db_serialize(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    emp_id = serializers.CharField(source='emp.id_number', read_only=True)
    full_name = serializers.CharField(source='emp.pi.user.get_fullname', read_only=True)
    emp_status = serializers.CharField(source='emp.empstatus.name',read_only=True, allow_null=True)
    division = serializers.CharField(source='emp.section.div.div_name', read_only=True, allow_null=True)
    typeofassistant = serializers.CharField(read_only=True)
    particular = serializers.CharField(read_only=True, allow_null=True)
    amount_excess = serializers.CharField(read_only=True,allow_null=True)
    amount_extended = serializers.CharField(read_only=True, allow_null=True)
    relationship = serializers.CharField(read_only=True, allow_null=True)
    share_contrib = serializers.CharField(read_only=True, allow_null=True)
    period_applied = serializers.DateField(format="%b %d, %Y", read_only=True)
    entry = serializers.IntegerField(read_only=True)
    class Meta:
        model = sweap_assistance
        fields = ['id','emp_id','full_name','emp_status','division','typeofassistant','particular','amount_excess','amount_extended','relationship','share_contrib', \
                   'period_applied','entry']

class emp_assistance_serialize(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    emp_id = serializers.CharField(source='emp.id_number', read_only=True)
    lname = serializers.CharField(source='emp.pi.user.last_name')
    fname = serializers.CharField(source='emp.pi.user.first_name')
    mname = serializers.CharField(source='emp.pi.user.middle_name')
    employment_status = serializers.CharField(source='emp.empstatus.name', read_only=True, allow_null=True)
    division = serializers.CharField(source='emp.section.div.div_name', read_only=True, allow_null=True)
    rq_date = serializers.DateField(format="%b %d, %Y", read_only=True)
    sex = serializers.CharField(source='emp.pi.gender')
    class Meta:
        model = employee_assistance_sop
        fields = ['id','emp_id','lname','fname','mname','division', 'rq_date','sex','employment_status']

class health_profile_serialize(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    emp_id = serializers.CharField(source='emp.id_number', read_only=True)
    fname = serializers.CharField(source='emp.pi.user.first_name')
    lname = serializers.CharField(source='emp.pi.user.last_name')
    mname = serializers.CharField(source='emp.pi.user.middle_name')
    division = serializers.CharField(source='emp.section.div.div_name', read_only=True, allow_null=True)
    category = serializers.CharField(read_only=True)
    class Meta:
        model = health_profile
        fields = ['id','emp_id','fname','lname','mname','division','category']

class sweap_gratuity_serialize(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    emp_id = serializers.CharField(source='emp.id_number', read_only=True)
    fname = serializers.CharField(source='emp.pi.user.first_name')
    lname = serializers.CharField(source='emp.pi.user.last_name')
    mname = serializers.CharField(source='emp.pi.user.middle_name')
    division = serializers.CharField(source='emp.section.div.div_name', read_only=True, allow_null=True)
    type_of_assistance = serializers.CharField(read_only=True)
    emp_yearinservice = serializers.CharField(read_only=True)
    share_contrib = serializers.CharField(read_only=True)
    amount_recieved = serializers.CharField(read_only=True)
    class Meta:
        model = sweap_gratuity
        fields = ['id', 'emp_id','lname','fname','mname','division', 'type_of_assistance','emp_yearinservice','share_contrib', 'amount_recieved']

class incident_report_serialize(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    emp_id = serializers.CharField(source='emp.id_number', read_only=True)
    fname = serializers.CharField(source='emp.pi.user.first_name')
    lname = serializers.CharField(source='emp.pi.user.last_name')
    mname = serializers.CharField(source='emp.pi.user.middle_name')
    employment_status = serializers.CharField(source='emp.empstatus.name', read_only=True, allow_null=True)
    division = serializers.CharField(source='emp.section.div.div_name', read_only=True, allow_null=True)
    sex = serializers.CharField(source='emp.pi.gender')
    date = serializers.DateField(format="%b %d, %Y", read_only=True)
    category= serializers.CharField(source='category.name')

    class Meta:
        model = incidentreport_db
        fields = ['id', 'emp_id','fname','lname','mname','category', 'employment_status', 'division','sex','date']