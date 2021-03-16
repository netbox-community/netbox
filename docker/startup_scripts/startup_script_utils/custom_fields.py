def set_custom_fields_values(entity, custom_field_data):
  if not custom_field_data:
    return

  entity.custom_field_data = custom_field_data
  return entity.save()

def pop_custom_fields(params):
  if 'custom_field_data' in params:
    return params.pop('custom_field_data')
  elif 'custom_fields' in params:
    print("⚠️ Please rename 'custom_fields' to 'custom_field_data'!")
    return params.pop('custom_fields')

  return None
