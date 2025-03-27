from comic_be.apps.comic.serializers_container import (
    UserComic, serializers, timezone
)


class UserComicSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserComic
        fields = '__all__'


class UserComicCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserComic
        fields = ['comic', 'is_favorite', 'is_like', 'rating', 'created_at', 'updated_at']

    @staticmethod
    def validate_rating(rating):
        if rating < 0 or rating > 5:
            raise serializers.ValidationError('Rating must be between 0 and 5')
        return rating

    @staticmethod
    def update_comic(comic, validated_data):
        review = comic.reviews
        if validated_data['is_like']:
            review['likes'] += 1
        if validated_data['rating']:
            if review['rating']:
                review['rating'] = ((validated_data['rating'] * review['number_of_user_rating'] + validated_data['rating'])
                                    / review['number_of_user_rating'] + 1)
            else:
                review['rating'] = validated_data['rating']
            review['number_of_user_rating'] += 1
        comic.reviews = review
        comic.save()

    def create(self, validated_data):
        current_user = self.context['request'].user
        user_comic = UserComic.objects.create(**validated_data, user=current_user,
                                              created_at=timezone.now(), updated_at=timezone.now())
        self.update_comic(user_comic.comic, validated_data)
        return user_comic
