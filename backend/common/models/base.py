from django.db import models
from django.conf import settings
from django.utils.text import slugify


# ========================================
# SLUG MODEL
# ========================================
class SlugModel(models.Model):
    """Abstract model that adds automatic slug generation"""
    
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
    )

    SLUG_SOURCE_FIELD = "name"

    class Meta:
        abstract = True

    def generate_unique_slug(self):
        """Generate a unique slug based on the source field"""
        value = getattr(self, self.SLUG_SOURCE_FIELD)

        base_slug = slugify(value)
        slug = base_slug

        counter = 1

        ModelClass = self.__class__

        while ModelClass.objects.filter(
            slug=slug
        ).exclude(
            pk=self.pk
        ).exists():

            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)



# ========================================
# GENERAL MODEL WITHOUT SLUG
# ========================================
class GeneralModelWithoutSlug(models.Model):
    """
    Base model with timestamps, user tracking, and common fields
    but without slug generation
    """
    
    # Timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )
    
    # User tracking fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",
        help_text="User who created this record"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated",
        help_text="User who last updated this record"
    )
    
    # Common fields
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this record is active"
    )
    
    class Meta:
        abstract = True
    
    def soft_delete(self, deleted_by=None):
        """Soft delete by setting is_active to False"""
        self.is_active = False
        if deleted_by:
            self.updated_by = deleted_by
        self.save()
    
    def activate(self, activated_by=None):
        """Activate the record"""
        self.is_active = True
        if activated_by:
            self.updated_by = activated_by
        self.save()
    
    @property
    def is_deleted(self):
        """Check if record is soft-deleted"""
        return not self.is_active



# ========================================
# GENERAL MODEL (Combined)
# ========================================
class GeneralModel(SlugModel):
    """
    Complete abstract base model that includes:
    - Timestamps (created_at, updated_at)
    - User tracking (created_by, updated_by)
    - Slug generation
    - Active status (common field)
    - Notes field (common field)
    """
    
    # Timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )
    
    # User tracking fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_created",
        help_text="User who created this record"
    )
    
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updated",
        help_text="User who last updated this record"
    )
    
    # Common fields for many ERP models
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this record is active"
    )
    
    # Meta configuration
    class Meta:
        abstract = True

    
    def soft_delete(self, deleted_by=None):
        """Soft delete by setting is_active to False"""
        self.is_active = False
        if deleted_by:
            self.updated_by = deleted_by
        self.save()
    
    def activate(self, activated_by=None):
        """Activate the record"""
        self.is_active = True
        if activated_by:
            self.updated_by = activated_by
        self.save()
    
    @property
    def is_deleted(self):
        """Check if record is soft-deleted"""
        return not self.is_active


# ========================================
# CODE MODEL
# ========================================
class GeneralCodeModel(GeneralModel):
    """
    Base model for objects that need a unique code (SKU, Batch Code, etc.)
    """
    
    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique code identifier"
    )
    
    class Meta:
        abstract = True

class SimpleCodeModel(GeneralModelWithoutSlug):
    """
    Base model for objects that need a unique code (SKU, Batch Code, etc.)
    """
    
    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique code identifier"
    )
    
    class Meta:
        abstract = True
    


# ========================================
# SKU MODEL
# ========================================
class GeneralSKUModel(GeneralModel):
    """
    Base model for objects that need a unique code (SKU, Batch Code, etc.)
    """
    
    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique sku identifier"
    )
    
    class Meta:
        abstract = True

class SimpleSKUModel(GeneralModelWithoutSlug):
    """
    Base model for objects that need a unique code (SKU, Batch Code, etc.)
    """
    
    sku = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique sku identifier"
    )
    
    class Meta:
        abstract = True
