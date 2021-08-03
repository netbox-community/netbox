import graphene

__all__ = (
    'ImageAttachmentsMixin',
)


class ImageAttachmentsMixin:
    image_attachments = graphene.List('extras.graphql.types.ImageAttachmentType')

    def resolve_image_attachments(self, info):
        return self.images.restrict(info.context.user, 'view')
