from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .adminforms import PostAdminForm

from .models import Post, Category, Tag


# Register your models here.

class PostInline(admin.StackedInline):
	fields = ('title', 'desc')
	extra = 1
	model = Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	inlines = [PostInline, ]
	list_display = ('name', 'status', 'is_nav', 'created_time', 'owner')
	fields = ('name', 'status', 'is_nav')

	def save_model(self, request, obj, form, change):
		obj.owner = request.user
		return super(CategoryAdmin, self).save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	list_display = ('name', 'status', 'created_time', 'owner')
	fields = ('name', 'status')

	def save_model(self, request, obj, form, change):
		obj.owner = request.user
		return super(TagAdmin, self).save_model(request, obj, form, change)


class CategoryOwnerFilter(admin.SimpleListFilter):
	title = '分类过滤器'
	parameter_name = 'owner_category'

	def lookups(self, request, model_admin):
		return Category.objects.filter(owner=request.user).values_list('id', 'name')

	def queryset(self, request, queryset):
		category_id = self.value()
		if category_id:
			return queryset.filter(category_id=self.value())
		return queryset


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	form = PostAdminForm
	list_display = [
		'title', 'category', 'status',
		'created_time', 'owner', 'operator'
	]
	list_display_links = []
	list_filter = [CategoryOwnerFilter, ]
	search_fields = ['title', 'category__name']

	save_on_top = True

	# fields = (
	# 	('category', 'title'),
	# 	'desc',
	# 	'status',
	# 	'content',
	# 	'tag',
	# )
	# fieldsets = ((名称,{内容}),(名称,{内容}))
	fieldsets = (
		('基础配置', {
			'description': '基础配置描述',
			'fields': (
				('title', 'category'),
				'status',
			),
		}),
		('内容', {
			'fields': (
				'desc',
				'content',
			),
		}),
		('额外信息', {
			'classes': ('collapse',),
			'fields': ('tag',)
		})
	)
	# filter_horizontal = ('tag', ) # 多对多字段横向展示
	# filter_vertical = ('tag', ) # 多对多字段纵向展示

	def operator(self, obj):
		return format_html('<a href="{}">编辑</a>', reverse('admin:blog_post_change', args=(obj.id,)))

	operator.short_description = '操作'

	def save_model(self, request, obj, form, change):
		obj.owner = request.user
		return super(PostAdmin, self).save_model(request, obj, form, change)

	def get_queryset(self, request):
		qs = super(PostAdmin, self).get_queryset(request)
		return qs.filter(owner=request.user)
