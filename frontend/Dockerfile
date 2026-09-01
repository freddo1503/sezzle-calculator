# The interface, as a production build served statically. No development server
# and no bind mounts: development happens on the host (just dev), and this image
# exists so an evaluator can run the whole stack with one command.
FROM node:slim AS build

WORKDIR /app
RUN npm install --global pnpm

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

HEALTHCHECK --interval=5s --timeout=3s --retries=10 \
  CMD wget --quiet --spider http://127.0.0.1:80/ || exit 1
