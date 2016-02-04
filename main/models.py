from django.db import models


class DictCMU(models.Model):
    entry = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    variant = models.IntegerField(null=True, blank=True)
    char_length = models.IntegerField(null=True, blank=True)
    phonemes = models.CharField(max_length=255, null=True, blank=True)
    list_length = models.IntegerField(null=True, blank=True)
    phonemes_no_num = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=25, null=True, blank=True)

    def __unicode__(self):
        return self.entry
