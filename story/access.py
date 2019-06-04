class ObjectPermissionsBackend:
  def has_perm(self, user_obj, perm, obj=None):
    if obj is None:
      return False
    if perm == 'story.add_post':
      return True;
    elif perm == 'story.view_post':
      return self.has_view_perm(user_obj, obj)
    elif perm == 'story.change_post' or perm == 'story.delete_post':
      return self.has_change_perm(user_obj, obj)

  def has_view_perm(self, user_obj, obj):
    if obj.viewed_by == 'all':
      return True
    elif obj.viewers.intersection(user_obj.groups.all()):
        return True
    return False

  def has_change_perm(self, user_obj, obj):
    return user_obj.groups.all().filter(id=obj.knower.id).exists()
