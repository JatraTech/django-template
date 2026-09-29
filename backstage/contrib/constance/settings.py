BACKSTAGE_CONSTANCE_ADDITIONAL_FIELDS = {
    str: [
        "django.forms.CharField",
        {
            "widget": "backstage.widgets.BackstageAdminTextInputWidget",
            "required": False,
        },
    ],
    int: [
        "django.forms.IntegerField",
        {
            "widget": "backstage.widgets.BackstageAdminIntegerFieldWidget",
        },
    ],
    float: [
        "django.forms.FloatField",
        {
            "widget": "backstage.widgets.BackstageAdminDecimalFieldWidget",
        },
    ],
    bool: [
        "django.forms.BooleanField",
        {
            "widget": "backstage.widgets.BackstageBooleanSwitchWidget",
            "required": False,
        },
    ],
    "file_field": [
        "django.forms.fields.FileField",
        {
            "widget": "backstage.widgets.BackstageAdminFileFieldWidget",
        },
    ],
    "image_field": [
        "django.forms.fields.ImageField",
        {
            "widget": "backstage.widgets.BackstageAdminImageFieldWidget",
        },
    ],
}
